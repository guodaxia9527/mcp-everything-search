import ctypes
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(BASE_DIR, "Everything64.dll")
print(f"Loading DLL from: {dll_path}")

try:
    lib = ctypes.WinDLL(dll_path)
    print("DLL loaded successfully")
    major = lib.Everything_GetMajorVersion()
    print(f"Major Version: {major}")
except Exception as e:
    print(f"Error: {e}")
