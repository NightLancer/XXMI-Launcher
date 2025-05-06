import sys
import logging
import multiprocessing
import time

from pathlib import Path


def verify_msvc_integrity():
    """
    Does basic integrity checks of Microsoft Visual C++ Redistributable
    """

    try:
        import ctypes
    except BaseException as e:
        raise Exception(f'Failed to verify ctypes import!') from e

    msvc_dlls = [
        'msvcp140.dll',  # Common VC++ 2015-2022 DLL
        'vcruntime140.dll',  # Runtime DLL
        'vcruntime140_1.dll',  # Runtime DLL
        'ucrtbase.dll',  # Universal C Runtime DLL
    ]
    msvc_dll_handles = []

    # Check existence of MSVC++ DLLs
    for dll in msvc_dlls:
        try:
            # Load DLL from default path
            win_dll = ctypes.WinDLL(dll)
            # Cast DLL handle as c_void_p to adjust it to the platform’s bitness (32-bit or 64-bit)
            dll_handle = ctypes.cast(win_dll._handle, ctypes.c_void_p)
            # Store DLL handle for later version verification
            msvc_dll_handles.append((dll, dll_handle))
        except BaseException as e:
            raise Exception(f'Failed to verify {dll}!') from e

    # Try to load GetFileVersionInfo from win32api package
    # It's a good way to check MSVC++ by itself, as win32api requires it to function
    try:
        from win32api import GetFileVersionInfo, HIWORD, LOWORD
    except BaseException as e:
        raise Exception(f'Failed to verify win32api import!') from e

    if not callable(GetFileVersionInfo):
        raise Exception(f'Failed to verify GetFileVersionInfo being function!')
    if not callable(HIWORD):
        raise Exception(f'Failed to verify HIWORD being function!')
    if not callable(LOWORD):
        raise Exception(f'Failed to verify LOWORD being function!')

    # Create buffer to store path of loaded DLLs
    try:
        dll_path_buffer = ctypes.create_unicode_buffer(1024)

        # Read DLL versions
        dll_versions = []

        for (dll, dll_handle) in msvc_dll_handles:

            # Read path to loaded DLL from handle
            ctypes.windll.kernel32.GetModuleFileNameW(dll_handle, dll_path_buffer, 1024)

            # Get DLL version info
            version_info = GetFileVersionInfo(str(dll_path_buffer.value), '\\')

            ms_file_version = version_info['FileVersionMS']
            ls_file_version = version_info['FileVersionLS']

            version = [str(HIWORD(ms_file_version)), str(LOWORD(ms_file_version)),
                       str(HIWORD(ls_file_version)), str(LOWORD(ls_file_version))]

            dll_versions.append(f'{dll}: {".".join(version)}')

        logging.debug(f'Using MSVC++ DLLs: {str(dll_versions)}')

    except BaseException:
        pass


if __name__ == '__main__':
    # Multiprocessing support for Pyinstaller
    multiprocessing.freeze_support()

    if '__compiled__' in globals():
        # Nuitka (release build): `XXMI Launcher\Resources\Bin\XXMI Launcher.exe`
        root_path = Path(sys.argv[0]).resolve().parent.parent.parent
    elif getattr(sys, 'frozen', False):
        # Pyinstaller (debug build): `XXMI Launcher\Resources\Bin\XXMI Launcher.exe`
        root_path = Path(sys.executable).parent.parent.parent
    else:
        # Python (native): `XXMI Launcher\src\xxmi_launcher\app.py`
        root_path = Path(__file__).resolve().parent.parent.parent

    instance_id = int(time.time() * 1000) % 1000000

    logging.basicConfig(filename=root_path / 'XXMI Launcher Log.txt',
                        encoding='utf-8',
                        filemode='a',
                        format=f'%(asctime)s {instance_id:06} %(name)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    logging.debug(f'App Start')

    try:
        try:
            verify_msvc_integrity()
        except Exception as e:
            raise Exception(f'MSVC++ Redistributable is damaged or not installed!\n\n'
                            f'Please reintall it from https://aka.ms/vs/17/release/vc_redist.x64.exe\n\n'
                            f'ERROR: {e}') from e

        import core.path_manager as Paths
        Paths.initialize(root_path)

        import gui.windows.main.main_window as main_window
        gui = main_window.MainWindow()

        from core.application import Application
        Application(gui)

    except BaseException as e:
        logging.exception(e)
        import traceback
        from tkinter.messagebox import showerror
        showerror(title='XXMI Launcher - Fatal Error',
                  message=f'{e}\n\n'
                          f'{traceback.format_exc()}')
