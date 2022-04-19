import logging, os, sys
import ctypes.wintypes, pathlib

def log_PyInstaller_state(logger):
    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        sys.path.insert(1, os.path.join(sys.path[0], '../shared'))
        logger.info("NetAdmin from source")
    else:
        logger.info("NetAdmin running from .exe, "+"MEIPASS - "+getattr(sys, '_MEIPASS'))

def setup_logger(name="mainlogger"):
    '''
    Setups a new logger according to the specified name -
     1. The logger will also log to a file called "client_log.log" found in User/Documents/NetAdmin/client_files.
     2. The format for the logger is also set-up.
     3. Logger level is set to DEBUG.
    Returns: the instance of the logger created.

    '''
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # --- create file handler
    # get document folder path and put into loggerdir
    CSIDL_PERSONAL = 5  #
    SHGFP_TYPE_CURRENT = 0
    od = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, od)
    loggerDir = ""
    for c in od:
        if c == '\0':
            break
        loggerDir += c

    # add NetAdmin/client_files/client_log.log to path
    loggerDir = os.path.join(loggerDir, "NetAdmin\\client_files")
    pathlib.Path(loggerDir).mkdir(parents=True, exist_ok=True)
    loggerDir = os.path.join(loggerDir, "client_log.log")

    fh = logging.FileHandler(loggerDir)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d')
    fh.setFormatter(formatter)

    # add file handler to main logger
    logger.addHandler(fh)

    logger.info("Logger initialized")