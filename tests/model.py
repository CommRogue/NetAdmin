import os

path = "C:\\Program Files\\Adobe\\Common\\Plug-ins\\7.0\\MediaCore"

with os.scandir(path) as it:
    for entry in it:
        print(entry.name)