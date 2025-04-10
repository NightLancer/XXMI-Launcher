import logging
import os

from multiprocessing import Process, Array


def is_wine():
    #return any(x in os.environ for x in ['WINE', 'WINEPREFIX', 'WINELOADER'])
    return False


def log_system_info():
    # try:
        # process = SystemInfoProcess()
        # process.start()
        # process.join()
        # logging.info(f'System: {process.data.raw.decode('utf-8')[:process.data.raw.find(b'\0')]}')
    # except Exception as e:
        # logging.exception(e)
    logging.info('***System info***')


class SystemInfoProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.data = Array('c', b'\0' * 512)

    def run(self):
        result = {}

        # try:
            # result['Platform'] = f'{os.name.upper()}{'+WINE' if is_wine() else ''}'
        # except Exception:
            # result['Platform'] = 'Unknown'
        result['Platform'] = 'Windows'

        # try:
            # import wmi
            # pc = wmi.WMI()
        # except Exception as e:
            # import traceback
            # error = f'WMI initialization failed on {result['Platform']} platform: {e}\n\n{traceback.format_exc()}'
            # self.data.raw = error.encode('utf-8')
            # return

        try:
            os_info = pc.Win32_OperatingSystem()[0]
        except Exception:
            pass

        # try:
            # result['OS'] = f'{os_info.Name.encode('utf-8').split(b'|')[0].decode('utf-8')} {os_info.Version}'
        # except Exception:
        result['OS'] = 'Unknown'

        # try:
            # result['CPU'] = pc.Win32_Processor()[0].Name.strip()
        # except Exception:
        result['CPU'] = 'Unknown'

        try:
            free_ram = round(float(os_info.FreePhysicalMemory) / 1048576, 2)
            total_ram = round(float(os_info.TotalVisibleMemorySize) / 1048576, 2)
            result['RAM'] = f'{free_ram}/{total_ram} GB'
        except Exception:
            result['RAM'] = 'Unknown'

        try:
            gpu_info = []
            for gpu in list(pc.Win32_VideoController()):
                gpu_info.append(gpu.Name.strip())
            result['GPU'] = ', '.join(gpu_info)
        except Exception:
            result['GPU'] = 'Unknown'

        try:
            result['MB'] = pc.Win32_ComputerSystem()[0].model
        except Exception:
            result['MB'] = 'Unknown'

        self.data.raw = str(result).encode('utf-8')
