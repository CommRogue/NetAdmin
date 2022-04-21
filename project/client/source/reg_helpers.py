import winreg
import statics

def set_autorun_reg(key):
    winreg.SetValueEx(key, "NetAdmin", 0, winreg.REG_BINARY,
                      statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe --run_main")

def set_encryption_key(id):
    """
    Creates or modifies an existing registry key specifying the encryption of the client.
    Args:
        id: the encryption key to be set or modified to.
    """
    key = winreg.CreateKey(*statics.REGISTRY_KEY_PATH)
    winreg.SetValue(key, 'EKey', winreg.REG_SZ, id)


def get_encryption_key():
    """
    Gets the encryption key of the client. Raises an exception if the key does not exist.

    Returns: the encryption key  found in the registry or None if not found.

    """
    key = winreg.OpenKey(*statics.REGISTRY_KEY_PATH)
    return winreg.QueryValue(key, 'EKey')


def set_id(id):
    """
    Creates or modifies an existing registry key specifying the UUID of the client.
    Args:
        id: the uuid to be set or modified to.
    """
    key = winreg.CreateKey(*statics.REGISTRY_KEY_PATH)
    winreg.SetValue(key, 'UUID', winreg.REG_SZ, id)


def get_id():
    """
    Gets the UUID of the client. Raises an exception if the key does not exist.

    Returns: the uuid found in the registry or None if not found.

    """
    key = winreg.OpenKey(*statics.REGISTRY_KEY_PATH)
    return winreg.QueryValue(key, 'UUID')