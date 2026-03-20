import sys
import json
import subprocess
import os
import logging
import shlex
import ctypes
import time
import io
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict

# Force UTF-8 for stdin and stdout to handle Chinese characters on Windows
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Everything SDK Constants ---
EVERYTHING_REQUEST_FILE_NAME = 0x00000001
EVERYTHING_REQUEST_PATH = 0x00000002
EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
EVERYTHING_REQUEST_EXTENSION = 0x00000008
EVERYTHING_REQUEST_SIZE = 0x00000010
EVERYTHING_REQUEST_DATE_CREATED = 0x00000020
EVERYTHING_REQUEST_DATE_MODIFIED = 0x00000040
EVERYTHING_REQUEST_DATE_ACCESSED = 0x00000080
EVERYTHING_REQUEST_ATTRIBUTES = 0x00000100
EVERYTHING_REQUEST_FOLDER_SIZE = 0x00000200

EVERYTHING_SORT_NAME_ASCENDING = 1
EVERYTHING_SORT_NAME_DESCENDING = 2
EVERYTHING_SORT_PATH_ASCENDING = 3
EVERYTHING_SORT_PATH_DESCENDING = 4
EVERYTHING_SORT_SIZE_ASCENDING = 5
EVERYTHING_SORT_SIZE_DESCENDING = 6
EVERYTHING_SORT_EXTENSION_ASCENDING = 7
EVERYTHING_SORT_EXTENSION_DESCENDING = 8
EVERYTHING_SORT_DATE_CREATED_ASCENDING = 11
EVERYTHING_SORT_DATE_CREATED_DESCENDING = 12
EVERYTHING_SORT_DATE_MODIFIED_ASCENDING = 13
EVERYTHING_SORT_DATE_MODIFIED_DESCENDING = 14

SORT_MAP = {
    "name-asc": EVERYTHING_SORT_NAME_ASCENDING,
    "name-desc": EVERYTHING_SORT_NAME_DESCENDING,
    "path-asc": EVERYTHING_SORT_PATH_ASCENDING,
    "path-desc": EVERYTHING_SORT_PATH_DESCENDING,
    "size-asc": EVERYTHING_SORT_SIZE_ASCENDING,
    "size-desc": EVERYTHING_SORT_SIZE_DESCENDING,
    "extension-asc": EVERYTHING_SORT_EXTENSION_ASCENDING,
    "extension-desc": EVERYTHING_SORT_EXTENSION_DESCENDING,
    "date-modified-asc": EVERYTHING_SORT_DATE_MODIFIED_ASCENDING,
    "date-modified-desc": EVERYTHING_SORT_DATE_MODIFIED_DESCENDING,
}

# --- Logging Setup ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(BASE_DIR, "mcp_debug.log")
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

# --- Path Configuration ---
DLL_PATHS = [
    os.path.join(BASE_DIR, "Everything64.dll"),
    os.path.join(BASE_DIR, "Everything-SDK", "dll", "Everything64.dll"),
    os.path.join(BASE_DIR, "_internal", "Everything64.dll")
]
ENGINE_PATHS = [
    os.path.join(BASE_DIR, "everything.exe"),
    os.path.join(BASE_DIR, "Everything.exe"),
    os.path.join(BASE_DIR, "_internal", "everything.exe")
]

DEFAULT_SEARCH_LIMIT = 20
# [OPT] Max results stats will scan before aggregating — prevents OOM on huge drives
STATS_SCAN_LIMIT = 200_000


class EverythingSDK:
    def __init__(self, possible_dll_paths):
        self.lib = None
        for path in possible_dll_paths:
            if os.path.exists(path):
                try:
                    self.lib = ctypes.WinDLL(path)
                    self._setup_signatures()
                    logging.info(f"Loaded SDK from: {path}")
                    break
                except Exception as e:
                    logging.error(f"Failed to load DLL from {path}: {str(e)}")
        if not self.lib:
            logging.error("Everything64.dll not found.")

    def _setup_signatures(self):
        self.lib.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
        self.lib.Everything_SetRequestFlags.argtypes = [ctypes.c_uint32]
        self.lib.Everything_SetSort.argtypes = [ctypes.c_uint32]
        self.lib.Everything_QueryW.argtypes = [ctypes.c_bool]
        self.lib.Everything_QueryW.restype = ctypes.c_bool
        self.lib.Everything_GetNumResults.restype = ctypes.c_uint32
        self.lib.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_uint32, ctypes.c_wchar_p, ctypes.c_uint32]
        self.lib.Everything_GetResultSize.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint64)]
        self.lib.Everything_GetResultSize.restype = ctypes.c_bool
        self.lib.Everything_GetResultDateModified.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint64)]
        self.lib.Everything_GetResultDateModified.restype = ctypes.c_bool
        self.lib.Everything_GetLastError.restype = ctypes.c_uint32
        self.lib.Everything_GetMajorVersion.restype = ctypes.c_uint32
        self.lib.Everything_GetMinorVersion.restype = ctypes.c_uint32
        self.lib.Everything_SetMax.argtypes = [ctypes.c_uint32]
        self.lib.Everything_SetOffset.argtypes = [ctypes.c_uint32]

    def is_available(self):
        return self.lib is not None

    def get_version(self):
        if not self.is_available():
            return (0, 0)
        try:
            return (self.lib.Everything_GetMajorVersion(), self.lib.Everything_GetMinorVersion())
        except:
            return (0, 0)

    def is_engine_running(self):
        if not self.is_available():
            return False
        try:
            return self.lib.Everything_GetMajorVersion() > 0
        except:
            return False

    def ensure_engine(self, engine_paths):
        if self.is_engine_running():
            return True
        for engine_path in engine_paths:
            if os.path.exists(engine_path):
                logging.info(f"Starting engine: {engine_path}")
                try:
                    subprocess.Popen([engine_path, "-startup"], shell=False)
                    for _ in range(5):
                        time.sleep(1)
                        if self.is_engine_running():
                            return True
                except Exception as e:
                    logging.error(f"Launch failed: {str(e)}")
        return False

    def query_raw(self, search_text, sort_type=None,
                  request_flags=EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME,
                  max_results=None):
        if not self.is_available():
            return 0
        self.lib.Everything_SetSearchW(search_text)
        self.lib.Everything_SetRequestFlags(request_flags)
        if sort_type:
            self.lib.Everything_SetSort(sort_type)
        # [BUGFIX] Everything SDK is stateful: SetMax persists across queries.
        # A previous search with max_results=20 silently caps subsequent stats
        # queries. Always set explicitly: requested limit, or 0xFFFFFFFF to reset.
        try:
            self.lib.Everything_SetMax(max_results if max_results is not None else 0xFFFFFFFF)
        except Exception:
            pass
        if not self.lib.Everything_QueryW(True):
            return 0
        return self.lib.Everything_GetNumResults()


sdk = EverythingSDK(DLL_PATHS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def filetime_to_iso(ft):
    if ft == 0 or ft == 0xFFFFFFFFFFFFFFFF:
        return "Unknown"
    try:
        dt = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ft // 10)
        return dt.astimezone().isoformat()
    except:
        return "Unknown"


def format_size(size):
    if size == 0xFFFFFFFFFFFFFFFF:
        return "N/A"
    if size < 0:
        return "0.00 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def ok(data):
    """Return a successful structured JSON result."""
    return json.dumps({"status": "ok", **data}, ensure_ascii=False, indent=2)


def err(message, hint=None):
    """
    [OPT-STABILITY] Unified error envelope.
    Structured errors let any model parse failure reason reliably
    without regex-ing free text.
    """
    payload = {"status": "error", "message": message}
    if hint:
        payload["hint"] = hint
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Query builder
# ---------------------------------------------------------------------------

def build_smart_query(params):
    parts = []
    base_query = params.get("query", "").strip()
    if base_query and base_query != "*":
        parts.append(base_query)

    filename = params.get("filename", "").strip()
    if filename:
        if "*" not in filename and "?" not in filename and "regex:" not in filename:
            filename = f"*{filename}*"
        parts.append(filename)

    extension = params.get("extension", "").strip().lstrip("*.").lower()
    if extension:
        parts.append(f"ext:{extension}")

    path_limit = params.get("path", "").strip()
    if path_limit:
        path_limit = path_limit.replace("/", "\\")
        if ":" in path_limit and not path_limit.endswith("\\"):
            path_limit += "\\"
        parts.append(f"path:\"{path_limit}\"")

    return " ".join(parts) if parts else "*"


def parse_structured_params(params, raw_args=""):
    limit = params.get("limit", DEFAULT_SEARCH_LIMIT)
    sort_type = params.get("sort")
    flags = EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME
    if params.get("show_size"):
        flags |= EVERYTHING_REQUEST_SIZE
    if params.get("show_date"):
        flags |= EVERYTHING_REQUEST_DATE_MODIFIED
    actual_sort = SORT_MAP.get(sort_type)

    if sort_type and "size" in sort_type:
        flags |= EVERYTHING_REQUEST_SIZE
    if sort_type and "date" in sort_type:
        flags |= EVERYTHING_REQUEST_DATE_MODIFIED

    if raw_args:
        try:
            args = shlex.split(raw_args)
            i = 0
            while i < len(args):
                a = args[i].lower()
                if a == "-n" and i + 1 < len(args):
                    limit = int(args[i + 1])
                    i += 1
                elif a == "-sort" and i + 1 < len(args):
                    s = args[i + 1].lower().replace("descending", "desc").replace("ascending", "asc")
                    actual_sort = SORT_MAP.get(s)
                    i += 1
                elif a == "-size":
                    flags |= EVERYTHING_REQUEST_SIZE
                elif a in ["-dm", "-date-modified"]:
                    flags |= EVERYTHING_REQUEST_DATE_MODIFIED
                i += 1
        except:
            pass
    return {"limit": limit, "sort": actual_sort, "flags": flags}


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_everything(args):
    if not sdk.ensure_engine(ENGINE_PATHS):
        return err("Everything engine is not running.",
                   hint="Start Everything.exe manually or check ENGINE_PATHS config.")

    query_text = build_smart_query(args)
    if not query_text:
        return err("Query is empty.", hint="Provide at least one of: query, filename, extension, path.")

    p = parse_structured_params(args, args.get("raw_args", ""))

    # [OPT] Warn but still execute — don't block, just inform
    warnings = []
    if p["limit"] > 1000:
        warnings.append(
            "Large limit detected. For counting or folder aggregation use 'everything_stats' instead."
        )

    # [OPT] Guide toward better tool, but still return results
    if p["sort"] in [EVERYTHING_SORT_SIZE_ASCENDING, EVERYTHING_SORT_SIZE_DESCENDING] and p["limit"] <= 100:
        warnings.append(
            "Sorting files by size returns individual files. "
            "To find the largest FOLDERS use 'find_largest_folders' for accurate directory totals."
        )

    v = sdk.get_version()
    if v[0] >= 1 and v[1] >= 5:
        if "folder:" in query_text or p["sort"] in [EVERYTHING_SORT_SIZE_ASCENDING, EVERYTHING_SORT_SIZE_DESCENDING]:
            p["flags"] |= EVERYTHING_REQUEST_FOLDER_SIZE

    num_results = sdk.query_raw(query_text, sort_type=p["sort"],
                                request_flags=p["flags"], max_results=p["limit"])

    if num_results == 0:
        return _handle_zero_results(args, query_text)

    results = _collect_results(num_results, p)

    # [OPT-STABILITY] Always structured JSON — models parse this reliably
    # total_files_found = complete count from index, regardless of 'results_returned'
    # counting_tip = explicit guidance so models never increase limit just to count
    payload = {
        "query": query_text,
        "total_files_found": num_results,
        "results_returned": len(results),
        "truncated": num_results > len(results),
        "counting_tip": (
            "Use 'total_files_found' for the exact file count. "
            "Do NOT increase 'limit' just to count — it wastes memory. "
            "For multi-extension counting, call 'everything_stats' instead."
        ),
        "results": results,
    }
    if warnings:
        payload["warnings"] = warnings

    return ok(payload)


def _handle_zero_results(args, query_text):
    """
    [OPT] Separated from main search path for clarity.
    Returns structured error with actionable hints.
    """
    path_hint = args.get("path", "").strip()

    if path_hint and not os.path.exists(path_hint):
        return err(
            f"Path '{path_hint}' does not exist.",
            hint="Verify the directory path before searching."
        )

    if path_hint and ":" in path_hint:
        drive = path_hint.split(":")[0] + ":"
        if sdk.query_raw(f"folder:{drive}\\") == 0:
            return err(
                f"Drive {drive} is not indexed by Everything.",
                hint="Add it in Everything Options → Indexes → NTFS/Folders."
            )

    hints = []
    if "*" in query_text:
        hints.append("Try removing wildcards — Everything uses fuzzy matching by default.")
    if args.get("path") or args.get("extension"):
        raw_name = args.get("filename", "") or args.get("query", "")
        if raw_name and raw_name != "*":
            alt_count = sdk.query_raw(raw_name.replace("*", ""))
            if alt_count > 0:
                hints.append(
                    f"File exists elsewhere: unfiltered search found {alt_count} match(es). "
                    "Try removing the path or extension filter."
                )

    return ok({
        "query": query_text,
        "total_files_found": 0,
        "results_returned": 0,
        "truncated": False,
        "results": [],
        "hints": hints if hints else ["No files matched. Try a broader query."],
    })


def _collect_results(num_results, p):
    """Build the result list from Everything SDK results."""
    actual_limit = min(num_results, p["limit"])
    path_buf = ctypes.create_unicode_buffer(32768)
    size_val = ctypes.c_uint64()
    date_val = ctypes.c_uint64()
    results = []

    for i in range(actual_limit):
        item = {}
        sdk.lib.Everything_GetResultFullPathNameW(i, path_buf, 32768)
        item["path"] = path_buf.value

        if p["flags"] & EVERYTHING_REQUEST_SIZE:
            if sdk.lib.Everything_GetResultSize(i, ctypes.byref(size_val)):
                item["size"] = format_size(size_val.value)
                item["size_bytes"] = size_val.value

        if p["flags"] & EVERYTHING_REQUEST_DATE_MODIFIED:
            if sdk.lib.Everything_GetResultDateModified(i, ctypes.byref(date_val)):
                item["date_modified"] = filetime_to_iso(date_val.value)

        results.append(item)

    return results


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats(query, group_by="directory", sort_by="count", limit=10):
    if not sdk.ensure_engine(ENGINE_PATHS):
        return err("Everything engine is not running.")

    flags = EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME | EVERYTHING_REQUEST_SIZE
    v = sdk.get_version()
    if v[0] >= 1 and v[1] >= 5:
        flags |= EVERYTHING_REQUEST_FOLDER_SIZE

    num_results = sdk.query_raw(
        query,
        sort_type=EVERYTHING_SORT_SIZE_DESCENDING if sort_by == "size" else None,
        request_flags=flags,
    )

    if num_results == 0:
        return ok({"query": query, "group_by": group_by, "sort_by": sort_by, "results": []})

    counts = Counter()
    sizes = defaultdict(int)
    path_buf = ctypes.create_unicode_buffer(32768)
    size_val = ctypes.c_uint64()

    # [BUGFIX] Original had return inside loop — fixed: collect all, then return
    # [OPT] Cap scan at STATS_SCAN_LIMIT to prevent OOM on massive drives
    process_limit = min(num_results, STATS_SCAN_LIMIT)
    scanned = 0

    for i in range(process_limit):
        sdk.lib.Everything_GetResultFullPathNameW(i, path_buf, 32768)
        full_path = path_buf.value

        if group_by == "directory":
            key = full_path.rsplit('\\', 1)[0] if '\\' in full_path else full_path
        else:
            _, ext = os.path.splitext(full_path)
            key = ext.lower() if ext else "(no ext)"

        if sdk.lib.Everything_GetResultSize(i, ctypes.byref(size_val)):
            s = size_val.value
            if s != 0xFFFFFFFFFFFFFFFF:
                sizes[key] += s
        counts[key] += 1
        scanned += 1

    sorted_keys = sorted(
        sizes.items() if sort_by == "size" else counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    results = []
    for key, _ in sorted_keys[:limit]:
        results.append({
            "label": key,
            "file_count": counts[key],
            "total_size": format_size(sizes[key]),
            "total_size_bytes": sizes[key],
        })

    unique_groups = len(sorted_keys)

    return ok({
        "query": query,
        "group_by": group_by,
        "sort_by": sort_by,
        "total_files_found": num_results,
        "scanned": scanned,
        "truncated_scan": num_results > scanned,
        "unique_groups_found": unique_groups,
        "results_truncated": unique_groups > limit,
        "counting_tip": (
            "'total_files_found' is the definitive count for this query. "
            "No need to run 'everything_search' to verify — this number is authoritative. "
            "If 'results_truncated' is false, the results list is complete — "
            "few results means few matching groups, not a data quality issue."
        ),
        "size_note": "Size reflects direct child files only, not recursive folder totals.",
        "results": results,
    })


# ---------------------------------------------------------------------------
# Engine status
# ---------------------------------------------------------------------------

def get_engine_status():
    if not sdk.ensure_engine(ENGINE_PATHS):
        return err("Engine not running.")
    v = sdk.get_version()
    drives = []
    for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if sdk.query_raw(f"folder:{d}:\\") > 0:
            drives.append(f"{d}:")
    total = sdk.query_raw("*")
    return ok({
        "version": f"{v[0]}.{v[1]}",
        "indexed_drives": drives,
        "total_indexed_files": total,
        "engine_status": "healthy",
    })


# ---------------------------------------------------------------------------
# MCP protocol
# ---------------------------------------------------------------------------

# [OPT] Tool definitions extracted to a constant — easier to maintain and read
TOOLS = [
    {
        "name": "everything_search",
        "description": (
            "Search for files and folders by name, extension, or location. "
            "Use this when you need to FIND specific files or get the top N largest/newest files. "
            "NOT suitable for counting files or summarizing folder sizes — use 'everything_stats' for that.\n"
            "COUNTING TIP: 'total_files_found' in the response is ALWAYS the complete index count, "
            "independent of 'limit'. To count files of a type, use limit=1 and read 'total_files_found' — "
            "do NOT increase limit to millions just to count. "
            "For counting multiple extensions at once, use 'everything_stats'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Raw Everything search syntax (e.g. 'dm:today'). "
                        "Use only when semantic fields below are not enough."
                    ),
                },
                "filename": {
                    "type": "string",
                    "description": (
                        "File name to search for. Partial names are fine — wildcards added automatically. "
                        "Example: 'report' matches 'Q3_report_final.xlsx'."
                    ),
                },
                "extension": {
                    "type": "string",
                    "description": "File extension without dot. Example: 'mp4', 'pdf', 'docx'.",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "Limit search to this folder. "
                        "Example: 'D:\\\\Projects' or 'D:/Projects' (both work)."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of results to return. Default 20. Keep under 100 for speed.",
                    "default": DEFAULT_SEARCH_LIMIT,
                },
                "sort": {
                    "type": "string",
                    "description": (
                        "Sort order. Use 'size-desc' to find largest files. "
                        "Use 'date-modified-desc' to find most recently changed files."
                    ),
                    "enum": [
                        "name-asc", "name-desc",
                        "path-asc", "path-desc",
                        "size-asc", "size-desc",
                        "date-modified-asc", "date-modified-desc",
                    ],
                },
                "show_size": {
                    "type": "boolean",
                    "description": "Include file size in results.",
                },
                "show_date": {
                    "type": "boolean",
                    "description": "Include last-modified date in results.",
                },
                "raw_args": {
                    "type": "string",
                    "description": "Advanced: raw CLI flags (e.g. '-n 50 -sort size-desc'). Rarely needed.",
                },
            },
        },
    },
    {
        "name": "everything_stats",
        "description": (
            "FIRST CHOICE for any counting or aggregation task. "
            "Use this when the user asks: 'how many X files do I have?', "
            "'which folder has the most files?', 'what file types take the most space?'. "
            "The 'total_files_found' field in the response is the definitive count — "
            "do NOT follow up with 'everything_search' to verify it.\n"
            "MULTI-EXTENSION: call this tool once per extension and sum the results. "
            "Do NOT combine extensions with semicolons or commas in query — "
            "use 'ext:pdf' for PDF, 'ext:xlsx' for Excel, etc."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Filter which files to aggregate. Default '*' means all files. "
                        "Example: 'ext:mp4' to aggregate only videos. "
                        "Tip: add '-C:\\\\Windows' to exclude system files."
                    ),
                    "default": "*",
                },
                "group_by": {
                    "type": "string",
                    "enum": ["directory", "extension"],
                    "description": "'directory' groups by folder. 'extension' groups by file type.",
                    "default": "directory",
                },
                "sort_by": {
                    "type": "string",
                    "enum": ["count", "size"],
                    "description": "'count' ranks by number of files. 'size' ranks by total disk usage.",
                    "default": "count",
                },
                "limit": {
                    "type": "integer",
                    "description": "How many top results to return.",
                    "default": 10,
                },
            },
        },
    },
    {
        "name": "find_largest_folders",
        "description": (
            "Find the folders taking the most disk space. "
            "Use this when the user asks: 'what's eating my disk?', "
            "'which folders are largest?', 'help me free up space'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Optional. Leave empty to search ALL indexed drives at once. "
                        "Only set this to limit search to one specific drive or folder. "
                        "Example: 'C:\\\\' for whole C drive, 'D:\\\\Projects' for a subfolder."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of folders to return.",
                    "default": 5,
                },
            },
        },
    },
    {
        "name": "find_most_files",
        "description": (
            "Find folders containing the highest number of files. "
            "Use this when the user asks: 'where are files piling up?', "
            "'which folder has the most files?'."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Optional. Leave empty to search ALL indexed drives at once. "
                        "Only set this to limit to one specific drive or folder. "
                        "Example: 'D:\\\\'."
                    ),
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of folders to return.",
                    "default": 5,
                },
            },
        },
    },
    {
        "name": "get_engine_status",
        "description": (
            "Check if Everything engine is running, which drives are indexed, "
            "and total file count. Call this first if search returns unexpected errors."
        ),
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def send_json(data):
    sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle_request(request):
    req_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        send_json({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Everything-AllInOne-PRO", "version": "1.7.3"},
                "protocolVersion": "2024-11-05",
            },
        })

    elif method == "tools/list":
        send_json({"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}})

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "everything_search":
                result = search_everything(args)
            elif tool_name == "everything_stats":
                result = get_stats(
                    args.get("query", "*"),
                    args.get("group_by", "directory"),
                    args.get("sort_by", "count"),
                    args.get("limit", 10),
                )
            elif tool_name == "find_largest_folders":
                path_arg = args.get("path", "").strip()
                q = f"path:\"{path_arg}\"" if path_arg else "*"
                result = get_stats(q, group_by="directory", sort_by="size",
                                   limit=args.get("limit", 5))
            elif tool_name == "find_most_files":
                path_arg = args.get("path", "").strip()
                q = f"path:\"{path_arg}\"" if path_arg else "*"
                result = get_stats(q, group_by="directory", sort_by="count",
                                   limit=args.get("limit", 5))
            elif tool_name == "get_engine_status":
                result = get_engine_status()
            else:
                result = err(f"Unknown tool: {tool_name}",
                             hint=f"Available tools: {[t['name'] for t in TOOLS]}")

            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": result}]},
            })

        except Exception as e:
            logging.error(f"Execution error: {str(e)}", exc_info=True)
            send_json({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(e)},
            })


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle_request(json.loads(line))
        except Exception as e:
            logging.error(f"JSON Error: {str(e)}")