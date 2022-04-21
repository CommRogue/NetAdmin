import configparser, helpers
import traceback
import winreg, pathlib, statics, logging, runconfig, ctypes
from subprocess import Popen, PIPE
import typing
import reg_helpers
import sys, time, os, shutil

logger = logging.getLogger(statics.loggerName)


def gain_privileges_admin():
    if not helpers.is_admin():
        logger.info("NOT ADMIN")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
        sys.exit(0)
    else:
        logger.info("IS ADMIN!!!")

def clean_mei(): # use only after checking for frozen
    '''
    Deletes _MEI temporary folders created by PyInstaller, as long as they are not the current run's _MEI and they are older than 24 hours.
    '''
    if sys._MEIPASS:
        currentDirPath = sys._MEIPASS
        tempDirPath = currentDirPath.split("\\")
        tempDirPath.pop(-1)
        tempDirPath = '\\'.join(tempDirPath)
        dirs = [fname for fname in os.listdir(tempDirPath) if os.path.isdir(tempDirPath+"\\"+fname)]
        for dir in dirs:
            if dir.startswith("_MEI"):
                fullDirName = tempDirPath+"\\"+dir
                if fullDirName != currentDirPath:
                    ctime = os.path.getctime(fullDirName)
                    if time.time() - ctime > 1: # check if folder is older than 24 hours
                        shutil.rmtree(fullDirName)


def input_installation(path):
    ip, port, type = installer_dialog()
    if ip != -1:
        config = configparser.ConfigParser()
        config['CONNECTION'] = {'ip_or_hostname': ip, 'port': port, 'type': type}
        with open(path + "runconfig.ini", 'w+') as configfile:
            config.write(configfile)
    else:
        ctypes.windll.user32.MessageBoxW(0, "The NetAdmin client installation was cancelled.",
                                         "Installation Cancelled", 1)
        sys.exit(0)

def check_install():
    # TODO - verify that PROGRAMDATA folder has all the files necessary
    if os.path.exists(statics.PROGRAMDATA_NETADMIN_PATH):
        if not runconfig.get_runconfig(statics.PROGRAMDATA_NETADMIN_PATH): # check if config exists and also check its integrity
            return False
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

    gain_privileges_admin()

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

    ctypes.windll.user32.MessageBoxW(0,
                                     "The NetAdmin client has been uninstalled."
                                     ,"Uninstall Successful", 1)
    sys.exit(0)

def dashboard():
    import PySimpleGUI as sg
    import textwrap

    sg.theme('DarkAmber')   # Add a touch of color

    install_status = check_install()

    if install_status:
        install_status = "Installed"
    else:
        install_status = "Not Installed/Corrupted Installation"

    column_to_be_centered = [  [sg.Text('NetAdmin Client Dashboard', font=("Arial", 24))],
                    [sg.Text(f"Installation Status: {install_status}", font=("Arial", 12))],
                    [sg.Button('Install/Repair')],
                    [sg.Button("Uninstall")],
                    [sg.Button("Exit")]]

    layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
                  [sg.VPush()]]

    window = sg.Window('Window Title', layout, size=(500,300), finalize=True)

    window.TKroot.title("NetAdmin Client Dashboard")


    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == 'Install/Repair':
            install_and_run()
        elif event == 'Uninstall':
            uninstall()
        elif event == 'Exit' or event == sg.WIN_CLOSED:
            sys.exit(0)

def installer_dialog() -> typing.Tuple:
    import PySimpleGUI as sg
    import textwrap

    sg.theme('DarkAmber')   # Add a touch of color

    column_to_be_centered = [  [sg.Text('NetAdmin Manual Configurator', font=("Arial", 24))],
                    [sg.Text(' '.join(textwrap.wrap("Welcome to the NetAdmin manual installation. This window is shown because the manual installation option was chosen in the client executable creation process.", 60)), size=(60, None), font=("Arial", 10))],
                    [sg.Text("Address Type: ", font=("Arial", 12))],
                    [sg.Radio("IP", 1, key='-TYPE-', default=True, font=("Arial", 11)), sg.Radio("Hostname (DNS-Resolvable)", 1, key='-TYPE-', font=("Arial", 11))],
                    [sg.Text("Address:", font=("Arial", 12))],
                    [sg.InputText(key="-ADDRESS_IN-")],
                    [sg.Text("Port (default 49152):", font=("Arial", 12))],
                    [sg.InputText(key="-PORT_IN-", size=(10, 10))],
                    [sg.Button('OK')]]

    layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
                  [sg.VPush()]]

    window = sg.Window('Window Title', layout, size=(500,300), finalize=True)

    window.TKroot.title("NetAdmin Manual Configurator")


    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == 'OK': # if user closes window or clicks cancel
            if values['-PORT_IN-'] != "" and values['-ADDRESS_IN-'] != "":
                try:
                    int(values['-PORT_IN-'])
                except:pass
                else:
                    window.close()
                    return values['-ADDRESS_IN-'], values["-PORT_IN-"], "ip" if values['-TYPE-'] else "hostname"
        elif event == sg.WIN_CLOSED:
           return -1, -1, -1

def install_and_run():
    '''
    1. Copies the executable to ProgramData
    2. Adds to startup.
    3. Runs the program.

    '''
    logger.info("Installing NetAdmin....")

    gain_privileges_admin()

    # check if exe exists
    pathlib.Path(statics.PROGRAMDATA_NETADMIN_PATH).mkdir(parents=True, exist_ok=True)
    # if not os.path.isfile(BASE_PATH+"NetAdmin.exe"):
    #     # copy our file to the path
    #     logger.info("NetAdmin.exe not found in ProgramData. Copying NetAdmin.exe to ProgramData...")
    logger.info("Copying NetAdmin.exe to ProgramData...")
    try:
        shutil.copy(sys.executable, statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe")
    except:
        pass

    # verify that config file exists
    config = runconfig.get_runconfig(statics.PROGRAMDATA_NETADMIN_PATH)
    if not config:
        input_installation(statics.PROGRAMDATA_NETADMIN_PATH)

    # proc_arch = os.environ.get('PROCESSOR_ARCHITECTURE')
    # proc_arch64 = os.environ.get('PROCESSOR_ARCHITEW6432')

    # if proc_arch.lower() == 'x86' and not proc_arch64:
    #     arch_keys = {0}
    # elif proc_arch.lower() == 'x86' or proc_arch.lower() == 'amd64':
    #     arch_keys = winreg.KEY_WOW64_32KEY

    # add autorun on startup to registry
    key = None
    try:
        # TODO - check more about problems with differences between 64-bit and 32-bit windows registry values
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0,
                             winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
        reg_helpers.set_autorun_reg(key)
        logger.info("Added/Already added before autorun in registry")
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0,
                                         "The NetAdmin client installer encountered an error while trying to set a registry value to automatically run the application on this system's startup. "
                                         "Please make sure you are running this installer with administrator privileges and try again. "
                                         "The following error occured: \n "+traceback.format_exc(),
                                         "Installation Error", 1)
    finally:
        if key:
            winreg.CloseKey(key)

    ctypes.windll.user32.MessageBoxW(0, "The installation process has finished.", "Installation Complete", 0)

    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS = 0x00000008

    Popen([statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe", "-r"], stdin=PIPE, stdout=PIPE, stderr=PIPE,
          creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)

    sys.exit(0)

dashboard()