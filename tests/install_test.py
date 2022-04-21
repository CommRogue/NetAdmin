import os, winreg, statics, logging, installer, shutil, ctypes, reg_helpers
import traceback

logger = logging.getLogger("log")

def check_install():
    # TODO - verify that PROGRAMDATA folder has all the files necessary
    if os.path.exists(statics.PROGRAMDATA_NETADMIN_PATH):
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        try:
            i = 0
            while True:
                reg_value = winreg.EnumValue(key, i)
                name = str(reg_value[0])
                if name == "NetAdmin":
                    break
                i += 1
        except OSError:
            return False
        else:
            try:
                value = str(reg_value[1])
            except:
                return False
            else:
                return value == statics.AUTORUN_REG_VALUE
    else:
        return False


def uninstall():
    logger.info("Uninstalling NetAdmin....")

    installer.gain_privileges_admin()

    # check if programdata folder exists, and if so delete it
    if os.path.exists(statics.PROGRAMDATA_NETADMIN_PATH):
        shutil.rmtree(statics.PROGRAMDATA_NETADMIN_PATH)

    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        try:
            reg_helpers.delete_autorun_reg(key)
        except FileNotFoundError:
            pass
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0,
                                         "The NetAdmin client installer encountered an error while trying to delete a registry value to automatically run the application on this system's startup. "
                                         "Please make sure you are running this installer with administrator privileges and try again. "
                                         "The following error occured: \n " + traceback.format_exc(),
                                         "Uninstallation Error", 1)
    finally:
        if key:
            winreg.CloseKey(key)
uninstall()
print(check_install())