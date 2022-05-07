import FileExplorer
import OpenConnectionHelpers
import main
import screenshare
from SmartSocket import SmartSocket
import helpers
from NetProtocol import *
import threading

@helpers.try_connection
def receive(sock, proc):
    while True:
        data = sock.recv(1024)
        print(f"Got data: {data.decode()}")
        proc.stdin.write(data)
        proc.stdin.flush()
        proc.stdin.write("\n".encode())
        proc.stdin.flush()

@helpers.try_connection
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
                p = threading.Thread(target=screenshare.screenShareClient, args=(client, id, main.jpeg))
                p.start()
                break

            # if the request is to open a shell connection
            elif message['data'] == NetTypes.NetOpenShell.value:
                # open shell process
                #TODO - close process when openconnection ends
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
                OpenConnectionHelpers.sendallfiles(client, directory)

                # send file download end status
                client.send_message(NetMessage(NetTypes.NetStatus.value, NetStatus(NetStatusTypes.NetDownloadFinished.value)))