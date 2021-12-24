import win32api
from os import listdir
from os.path import isfile, join

drives = win32api.GetLogicalDriveStrings()
drives = drives.split('\000')[:-1]
files = [f for f in listdir(drives[0]) if not f.startswith('.')]
print(files)