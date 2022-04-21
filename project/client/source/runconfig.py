import configparser
import logging
from os import path

logger = logging.getLogger('mainlogger')

def verify_log_file_integrity(dir):
    '''
    Makes sure the correct fields are found in the logger file.
    Args:
        file: a textIO object of the config file.

    Returns: True if all fields are found, False otherwise.

    '''
    logger.debug("Verifying log file integrity")

    file = open(dir)
    config_parser = configparser.ConfigParser()
    config_parser.read_file(file)
    try:
        s = config_parser["CONNECTION"]['ip_or_hostname']
        s = config_parser["CONNECTION"]['type']
        s = config_parser["CONNECTION"]['port']
    except:
        return False
    else:
        return True


def get_runconfig(application_path):
    '''
    Tries to open the config file in the application path given (.exe directory), and if not found, then at the MUI directory.
    Also verifies that the config has the correct fields.
    Use only when frozen by PyInstaller.
    Args:
        application_path: directory of the application's .exe.

    Returns: the config directory if found and verified, None otherwise.

    '''
    # check if config is present in our directory
    dir = None
    try:
        dir = application_path + "runconfig.ini"
        open(dir, 'r')
        logger.info("Runconfig found at .exe's directory: " + application_path + "runconfig.ini")
    except:  # if file was not found
        try:
            dir = path.abspath(path.join(path.dirname(__file__), 'runconfig.ini'))
            open(dir, 'r')
            logger.info("Runconfig found at MUI folder")
        except:
            dir = None
    # check if
    if dir is not None:
        if verify_log_file_integrity(dir):
            return dir
        else:
            return None
    return dir