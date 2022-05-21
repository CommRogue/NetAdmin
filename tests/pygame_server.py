import os

scan = os.scandir('D:\\techem\\blyat_folder')

for item in scan:
    print(item)