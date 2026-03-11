import ctypes
import os

EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME = 0x00000004
dll_path = r"D:\soft\mcp-everything-search\Everything64.dll"
lib = ctypes.WinDLL(dll_path)

lib.Everything_SetSearchW.argtypes = [ctypes.c_wchar_p]
lib.Everything_QueryW.argtypes = [ctypes.c_bool]
lib.Everything_QueryW.restype = ctypes.c_bool
lib.Everything_GetNumResults.restype = ctypes.c_uint32
lib.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_uint32, ctypes.c_wchar_p, ctypes.c_uint32]

search_term = "爱"
print(f"Searching for: {search_term}")
lib.Everything_SetSearchW(search_term)
lib.Everything_SetRequestFlags(EVERYTHING_REQUEST_FULL_PATH_AND_FILE_NAME)

if lib.Everything_QueryW(True):
    num = lib.Everything_GetNumResults()
    print(f"Found {num} results.")
    if num > 0:
        buf = ctypes.create_unicode_buffer(1024)
        lib.Everything_GetResultFullPathNameW(0, buf, 1024)
        print(f"First result: {buf.value}")
else:
    print("Query failed.")
