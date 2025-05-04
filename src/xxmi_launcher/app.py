import sys
import logging
import multiprocessing
import time

from pathlib import Path


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

    # import binascii
    # arr = []
    # bytestring = binascii.unhexlify(''.join(arr))
    # test = bytestring.decode("ascii")

    instance_id = int(time.time() * 1000) % 1000000

    logging.basicConfig(filename=root_path / 'XXMI Launcher Log.txt',
                        encoding='utf-8',
                        filemode='a',
                        format=f'%(asctime)s {instance_id:06} %(name)s %(levelname)s %(message)s',
                        level=logging.DEBUG)

    logging.debug(f'App Start')

    try:
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
