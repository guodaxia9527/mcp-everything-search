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
EVERYTHING_REQUEST_FOLDER_SIZE = 0x00000200 # 1.5 Alpha+

# Sorting Constants
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
    "date-created-asc": EVERYTHING_SORT_DATE_CREATED_ASCENDING,
    "date-created-desc": EVERYTHING_SORT_DATE_CREATED_DESCENDING,
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

    def is_available(self):
        return self.lib is not None

    def get_version(self):
        if not self.is_available(): return (0, 0)
        try:
            return (self.lib.Everything_GetMajorVersion(), self.lib.Everything_GetMinorVersion())
        except: return (0, 0)

    def is_engine_running(self):
        if not self.is_available(): return False
        try:
            return self.lib.Everything_GetMajorVersion() > 0
        except: return False

    def ensure_engine(self, engine_paths):
        if self.is_engine_running(): return True
        for engine_path in engine_paths:
            if os.path.exists(engine_path):
                logging.info(f"Starting engine: {engine_path}")
                try:
                    subprocess.Popen([engine_path, "-startup"], shell=False)
                    for _ in range(5):
                        time.sleep(1)
                        if self.is_engine_running(): return True
                except Exception as e: logging.error(f"Launch failed: {str(e)}")
        return False

    def query_raw(self, search_text, sort_type=None, request_flags=EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME):
        if not self.is_available(): return 0
        self.lib.Everything_SetSearchW(search_text)
        self.lib.Everything_SetRequestFlags(request_flags)
        if sort_type: self.lib.Everything_SetSort(sort_type)
        if not self.lib.Everything_QueryW(True): return 0
        return self.lib.Everything_GetNumResults()

# Initialize
sdk = EverythingSDK(DLL_PATHS)

def filetime_to_iso(ft):
    if ft == 0 or ft == 0xFFFFFFFFFFFFFFFF: return "Unknown"
    try:
        dt = datetime(1601, 1, 1, tzinfo=timezone.utc) + timedelta(microseconds=ft // 10)
        return dt.isoformat()
    except: return "Unknown"

def format_size(size):
    if size == 0xFFFFFFFFFFFFFFFF: return "N/A"
    if size < 0: return "0.00 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024: return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def build_smart_query(params):
    """
    Assembles a semantic query from structured fields.
    Robustness: Expert query preserved; Filename auto-wrapped in wildcards for reliability.
    """
    parts = []
    
    # 1. Base query (Expert Mode) - Preserve everything including wildcards
    base_query = params.get("query", "").strip()
    if base_query and base_query != "*":
        parts.append(base_query)

    # 2. Semantic fields (Filename, Extension, Path)
    filename = params.get("filename", "").strip()
    if filename:
        # If no wildcards and not a regex hint, wrap in * for fuzzy matching
        if "*" not in filename and "?" not in filename and "regex:" not in filename:
            filename = f"*{filename}*"
        parts.append(filename)
        
    extension = params.get("extension", "").strip().lstrip("*.").lower()
    if extension:
        parts.append(f"ext:{extension}")
        
    path_limit = params.get("path", "").strip()
    if path_limit:
        # Normalize path for Everything engine
        if ":" in path_limit and not path_limit.endswith("\\"):
            path_limit += "\\"
        # Use quotes for paths with spaces
        parts.append(f"path:\"{path_limit}\"")

    return " ".join(parts)

def parse_structured_params(params, raw_args=""):
    limit = params.get("limit", 100)
    sort_type = params.get("sort")
    flags = EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME
    if params.get("show_size"): flags |= EVERYTHING_REQUEST_SIZE
    if params.get("show_date"): flags |= EVERYTHING_REQUEST_DATE_MODIFIED
    actual_sort = SORT_MAP.get(sort_type)
    
    if sort_type and "size" in sort_type: flags |= EVERYTHING_REQUEST_SIZE
    if sort_type and "date" in sort_type: flags |= EVERYTHING_REQUEST_DATE_MODIFIED

    if raw_args:
        try:
            args = shlex.split(raw_args)
            i = 0
            while i < len(args):
                a = args[i].lower()
                if a == "-n" and i+1 < len(args): limit = int(args[i+1]); i += 1
                elif a == "-sort" and i+1 < len(args):
                    s = args[i+1].lower().replace("descending", "desc").replace("ascending", "asc")
                    actual_sort = SORT_MAP.get(s); i += 1
                elif a == "-size": flags |= EVERYTHING_REQUEST_SIZE
                elif a in ["-dm", "-date-modified"]: flags |= EVERYTHING_REQUEST_DATE_MODIFIED
                i += 1
        except: pass
    return {"limit": limit, "sort": actual_sort, "flags": flags}

def search_everything(args):
    if not sdk.ensure_engine(ENGINE_PATHS): return "Everything engine is NOT running."
    
    query_text = build_smart_query(args)
    if not query_text: return "Query is empty."
    
    p = parse_structured_params(args, args.get("raw_args", ""))
    
    # PERFORMANCE WARNING & INTENT INTERCEPTION
    perf_prefix = ""
    if p["limit"] > 1000:
        perf_prefix = "WARNING: Requesting a large result limit is inefficient for AI. For counting or finding top folders, ALWAYS use 'everything_stats' instead.\n\n"
    
    # [AUTOPILOT]: Intercept size-based ranking intent
    if p["sort"] in [EVERYTHING_SORT_SIZE_ASCENDING, EVERYTHING_SORT_SIZE_DESCENDING] and p["limit"] <= 100:
        perf_prefix += "[SYSTEM GUIDANCE]: Detected size ranking intent. Note that 'everything_search' returns individual files. If you are looking for the 'largest FOLDERS', please use the dedicated 'find_largest_folders' tool for instant, accurate directory aggregation.\n\n"

    v = sdk.get_version()
    if v[0] >= 1 and v[1] >= 5:
        if "folder:" in query_text or (p["sort"] in [EVERYTHING_SORT_SIZE_ASCENDING, EVERYTHING_SORT_SIZE_DESCENDING]):
            p["flags"] |= EVERYTHING_REQUEST_FOLDER_SIZE

    num_results = sdk.query_raw(query_text, sort_type=p["sort"], request_flags=p["flags"])
    
    # --- ENHANCED DIAGNOSTICS & SELF-HEALING ---
    if num_results == 0:
        # 1. Drive check with Shielding
        path_hint = args.get("path", "").upper()
        if path_hint and ":" in path_hint:
            drive = path_hint.split(":")[0] + ":"
            if sdk.query_raw(f"path:\"{drive}\" limit:1") == 0:
                return f"ERROR: Drive {drive} is NOT indexed. Please add it in Everything Options -> Indexes -> NTFS/Folders.\n[SHIELD]: The disk is too large (millions of files). Standard OS commands (powershell, ls, dir) WILL HANG and TIMEOUT on this system. Please fix the Everything index instead."

        # 2. Expert Advice for AI
        advice = [f"Found 0 results for: '{query_text}'."]
        if "*" in query_text: advice.append("Hint: Try removing wildcards (*) as Everything uses fuzzy matching by default.")
        if args.get("path") or args.get("extension"):
            # Check if name exists anywhere else
            raw_name = args.get("filename", "") or args.get("query", "")
            if raw_name and raw_name != "*":
                alt_count = sdk.query_raw(raw_name.replace("*", ""), limit=1)
                if alt_count > 0:
                    advice.append(f"Note: This file exists in OTHER locations (unfiltered search found {alt_count} matches). Try removing path/extension filters.")
        
        return "\n".join(advice)
    
    return perf_prefix + render_results(num_results, p)

def render_results(num_results, p):
    actual_limit = min(num_results, p["limit"])
    lines = []
    path_buf = ctypes.create_unicode_buffer(32768)
    size_val = ctypes.c_uint64()
    date_val = ctypes.c_uint64()

    for i in range(actual_limit):
        parts = []
        if p["flags"] & EVERYTHING_REQUEST_SIZE:
            if sdk.lib.Everything_GetResultSize(i, ctypes.byref(size_val)):
                parts.append(f"[{format_size(size_val.value)}]")
        if p["flags"] & EVERYTHING_REQUEST_DATE_MODIFIED:
            if sdk.lib.Everything_GetResultDateModified(i, ctypes.byref(date_val)):
                parts.append(f"[{filetime_to_iso(date_val.value)}]")
        
        sdk.lib.Everything_GetResultFullPathNameW(i, path_buf, 32768)
        parts.append(path_buf.value)
        lines.append("  ".join(parts))
    
    return "\n".join(lines)

def get_stats(query, group_by="directory", sort_by="count", limit=10):
    if not sdk.ensure_engine(ENGINE_PATHS): return "Everything engine is NOT running."
    
    flags = EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME | EVERYTHING_REQUEST_SIZE
    v = sdk.get_version()
    if v[0] >= 1 and v[1] >= 5: flags |= EVERYTHING_REQUEST_FOLDER_SIZE

    num_results = sdk.query_raw(query, sort_type=EVERYTHING_SORT_SIZE_DESCENDING if sort_by=="size" else None, request_flags=flags)
    if num_results == 0: return "No matches."

    counts = Counter()
    sizes = defaultdict(int)
    path_buf = ctypes.create_unicode_buffer(32768)
    size_val = ctypes.c_uint64()
    
    process_limit = min(num_results, 1000000)
    for i in range(process_limit):
        sdk.lib.Everything_GetResultFullPathNameW(i, path_buf, 32768)
        full_path = path_buf.value
        
        if group_by == "directory":
            key = full_path.rsplit('\\', 1)[0] if '\\' in full_path else full_path
        else:
            dot_idx = full_path.rfind('.')
            key = full_path[dot_idx:].lower() if dot_idx != -1 and '\\' not in full_path[dot_idx:] else "(no ext)"

        if sdk.lib.Everything_GetResultSize(i, ctypes.byref(size_val)):
            s = size_val.value
            if s != 0xFFFFFFFFFFFFFFFF:
                sizes[key] += s
        counts[key] += 1

    sorted_keys = sorted(sizes.items() if sort_by == "size" else counts.items(), key=lambda x: x[1], reverse=True)
    res = []
    for key, _ in sorted_keys[:limit]:
        res.append({
            "label": key, 
            "count": counts[key], 
            "size_human": format_size(sizes[key]), 
            "size_bytes": sizes[key]
        })
    return json.dumps(res, indent=2, ensure_ascii=False)

def send_json(data):
    sys.stdout.write(json.dumps(data) + "\n")
    sys.stdout.flush()

def get_engine_status():
    if not sdk.ensure_engine(ENGINE_PATHS): return "Engine NOT running."
    v = sdk.get_version()
    # Find all indexed drives
    drives = []
    for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if sdk.query_raw(f"path:\"{d}:\\\" limit:1") > 0:
            drives.append(f"{d}:")
    
    total = sdk.query_raw("*")
    return {
        "version": f"{v[0]}.{v[1]}",
        "indexed_drives": drives,
        "total_files": total,
        "status": "Healthy"
    }

def handle_request(request):
    req_id = request.get("id")
    method = request.get("method")
    
    if method == "initialize":
        send_json({"jsonrpc": "2.0", "id": req_id, "result": {"capabilities": {"tools": {}}, "serverInfo": {"name": "Everything-AllInOne-PRO", "version": "1.6.2-AUTOPILOT"}, "protocolVersion": "2024-11-05"}})
    elif method == "tools/list":
        send_json({"jsonrpc": "2.0", "id": req_id, "result": {"tools": [
            {
                "name": "everything_search", 
                "description": "Find specific files. ULTRA-FAST. Use semantic fields (filename, extension) instead of guessing syntax. DO NOT use this for counting files or finding 'top' folders.", 
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Search query. Everything syntax supported (e.g. 'dm:today')."}, 
                        "filename": {"type": "string", "description": "Preferred: File name part to match (auto-wrapped in *)."},
                        "extension": {"type": "string", "description": "Preferred: Filter by extension (e.g. 'mp4', 'docx')."},
                        "path": {"type": "string", "description": "Optional: Restrict to directory (e.g. 'D:\\backup')."},
                        "limit": {"type": "integer", "description": "Max results. Keep LOW (<100) for efficiency. Do NOT use huge limits to count files.", "default": 20},
                        "sort": {
                            "type": "string", 
                            "enum": ["name-asc", "name-desc", "path-asc", "path-desc", "size-asc", "size-desc", "date-modified-asc", "date-modified-desc"]
                        },
                        "show_size": {"type": "boolean"},
                        "show_date": {"type": "boolean"},
                        "raw_args": {"type": "string"}
                    }
                }
            },
            {
                "name": "everything_stats", 
                "description": "CRITICAL for 'Top N' or counting tasks (e.g. 'most files', 'largest folders'). 1000x faster than manual counting. ALWAYS use this for aggregation.", 
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Filter files before aggregating. Tip: use '-C:\\Windows' to hide system clutter.", "default": "*"}, 
                        "group_by": {"type": "string", "enum": ["directory", "extension"], "description": "How to group files."}, 
                        "sort_by": {"type": "string", "enum": ["count", "size"], "description": "Sort metric."}, 
                        "limit": {"type": "integer", "description": "Max categories to return.", "default": 10}
                    }
                }
            },
            {
                "name": "find_largest_folders",
                "description": "DEPRECATED intent alias: Dedicated tool to find the largest directories on disk. Much faster and more accurate than manual search.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Scope the search to this directory (e.g. 'C:\\')"},
                        "limit": {"type": "integer", "description": "Number of folders to return", "default": 5}
                    }
                }
            },
            {
                "name": "find_most_files",
                "description": "DEPRECATED intent alias: Find directories containing the highest number of files. Useful for finding file hoards.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Scope the search to this directory (e.g. 'D:\\')"},
                        "limit": {"type": "integer", "description": "Number of folders to return", "default": 5}
                    }
                }
            },
            {
                "name": "get_engine_status",
                "description": "Check which drives are currently indexed and engine health.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]}})
    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        try:
            if tool_name == "everything_search":
                result = search_everything(args)
            elif tool_name == "everything_stats":
                result = get_stats(args.get("query", "*"), args.get("group_by", "directory"), args.get("sort_by", "count"), args.get("limit", 10))
            elif tool_name == "find_largest_folders":
                result = get_stats(f"path:\"{args.get('path', '*')}\"", group_by="directory", sort_by="size", limit=args.get("limit", 5))
            elif tool_name == "find_most_files":
                result = get_stats(f"path:\"{args.get('path', '*')}\"", group_by="directory", sort_by="count", limit=args.get("limit", 5))
            elif tool_name == "get_engine_status":
                result = json.dumps(get_engine_status(), indent=2)
            else: result = f"Unknown tool: {tool_name}"
            send_json({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": result}]}})


        except Exception as e:
            logging.error(f"Execution error: {str(e)}")
            send_json({"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})

if __name__ == "__main__":
    for line in sys.stdin:
        if not line: break
        try: handle_request(json.loads(line))
        except Exception as e: logging.error(f"JSON Error: {str(e)}")
