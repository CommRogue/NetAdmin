import ctypes, sys
import pathlib
from os import path
import logging
import os
import winreg, configparser, argparse, shutil
import subprocess

logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
# create file handler
fh = logging.FileHandler("C:\\Users\\guyst\\Documents\\logg.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add handler
logger.addHandler(fh)


# def get_runconfig(application_path):
#     # check if config is present in our directory
#     try:
#         f = open(application_path+"runconfig.ini", "r")
#         logger.info("runconfig.ini found at root: "+application_path+"runconfig.ini")
#     except:
#         try:
#             f = open(path.abspath(path.join(path.dirname(__file__), 'runconfig.ini')), 'r')
#             logger.info("runconfig.ini found at MUI")
#         except:
#             f = None
#     return f
#
# def is_admin():
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except:
#         return False

BASE_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\")
KEYLOG_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\keylog.txt")
CLIPBOARD_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\clipboard.txt")

def install(run=True):
    try:
        '''
        1. Copies the exeutable to ProgramData
        2. Adds to startup.
        Args:
            run: whether to run the client after installation
    
        '''
        logger.info("INSTALLING")
        print("Installing NetAdmin.... Please wait....")
        # display message box
        ctypes.windll.user32.MessageBoxW(0, "Installing...", "Your title", 1)

        if not is_admin():
            logger.info("NOT ADMIN")
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
            sys.exit(0)
        else:
            logger.info("IS ADMIN!!!")

        # check if exe exists
        pathlib.Path(BASE_PATH).mkdir(parents=True, exist_ok=True)
        # if not os.path.isfile(BASE_PATH+"NetAdmin.exe"):
        #     # copy our file to the path
        #     logger.info("NetAdmin.exe not found in ProgramData. Copying NetAdmin.exe to ProgramData...")
        shutil.copy(sys.executable, BASE_PATH+"NetAdmin.exe")

        # verify that config file exists
        config = get_runconfig(BASE_PATH)
        if not config:
            input_installation(BASE_PATH)

        # proc_arch = os.environ.get('PROCESSOR_ARCHITECTURE')
        # proc_arch64 = os.environ.get('PROCESSOR_ARCHITEW6432')

        # if proc_arch.lower() == 'x86' and not proc_arch64:
        #     arch_keys = {0}
        # elif proc_arch.lower() == 'x86' or proc_arch.lower() == 'amd64':
        #     arch_keys = winreg.KEY_WOW64_32KEY

        # check if registry value has been set
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        try:
            winreg.QueryValue(key, "NetAdmin")
        except Exception as e:
            print(e)
            # create registry value
            winreg.SetValueEx(key, "NetAdmin", 0, winreg.REG_SZ, BASE_PATH+"NetAdmin.exe --run_main")
            logger.info("NetAdmin.exe added to startup")
        else:
            logger.info("NetAdmin.exe already added to startup")
        winreg.CloseKey(key)
        ctypes.windll.user32.MessageBoxW(0, "The installation process has finished.", "Installation Complete", 0)
        os.system(BASE_PATH+"NetAdmin.exe -r")
        sys.exit(0)
    except Exception as e:
        logger.info(e)

def get_exe_directory():
    return os.path.dirname(sys.executable)+"\\"

def input_installation(path):
    print("Welcome to the NetAdmin manual installation. This window is shown because the manual installation option was chosen in the client executable creation process.")
    ip = input("IP: ")
    port = input("Port: ")
    config = configparser.ConfigParser()
    config['CONNECTION'] = {'ip': ip, 'port': port}
    with open(path + "runconfig.ini", 'w+') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    try:
        logger.info(BASE_PATH+"NetAdmin.exe")
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            logger.info("MAIN()")
        else:
            # handle arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("-r", "--run_main", help="Run the main() client function.", action='store_true')
            parser.add_argument("-i", "--install", help="Install the NetAdmin executable.", action='store_true')
            logger.info("args=%s" % str(sys.argv))
            args = parser.parse_args()
            if args.run_main:
                config = get_runconfig(get_exe_directory())
                if not config:
                    logger.info("ERROR: NO CONFIG FILE WAS FOUND. INSTALLATION CORRUPTED. ")
                else:
                    logger.info("MAIN()")
            else:
                install()
    except Exception as e:
        logger.info(e)