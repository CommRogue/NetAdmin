import os

def ActualDirectorySize(path, f):
    size = 0
    try:
        for dir in os.scandir(path):
            try:
                if dir.is_file():
                    size += dir.stat().st_size
                else:
                    size += ActualDirectorySize(dir.path, False)
            except:
                print("Error getting size of " + dir.path)
    except:
        print("Error getting size of " + path)
        if f:
            return 0  # signifying that the size of all accessible files (which is no files) is 0
    return size