import socket, _socket, struct, orjson, typing, fernet
from NetProtocol import NetMessage, NetProtocol

class SmartSocket(socket.socket):
    def __init__(self, key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Fkey = key
        if key:
            self.fernetInstance = fernet.Fernet(key)
        else:
            self.fernetInstance = None

    @staticmethod
    def _copy(sock):
        """
        Internal function to convert a socket object to a SmartSocket object.
        Works by duplicating the given socket resource, and giving it to the new SmartSocket object.
        Args:
            sock: socket object to be converted.

        Returns: the new SmartSocket object.

        """
        sResource = _socket.dup(sock.fileno())
        # None for SmartSocket Key
        sCopy = SmartSocket(None, sock.family, sock.type, sock.proto, fileno=sResource)
        sCopy.settimeout(sock.gettimeout())
        return sCopy

    def accept(self) -> typing.Tuple["SmartSocket", typing.Any]:
        connection, client_address = super().accept()
        SSObject = self._copy(connection)
        return SSObject, client_address

    def set_key(self, key):
        self.fernetInstance = fernet.Fernet(key)
        self.Fkey = key

    def receive_message(self) -> (int, typing.Any):
        """
        Receives a message from the socket. The message is size-appended and optionally encrypted.
        Returns: the size of the message, the orjson-loaded message, and whether the received message was encrypted.

        """
        try:
            size = self.receive_size()
            res = self.recv_exact(size, True)
            return size, orjson.loads(res[0]), res[1]
        except (ConnectionError, struct.error):
            return -1, -1, -1

    def send_message(self, data : NetMessage):
        """
        Sends a NetMessage through the socket. It will be size-appeneded and optionally encrypted.
        Args:
            data: the NetMessage to be sent.

        """
        super().send(self.packMessage(data))

    def send_appended_stream(self, data : bytes, encrypt=True, *args, **kwargs):
        if encrypt and self.fernetInstance:
            data = self.fernetInstance.encrypt(data)
        data = struct.pack(">I", len(data)) + data
        super().send(data, *args, **kwargs)

    def packMessage(self, message : NetMessage, encrypt=True) -> bytes:
        """
        Returns a byte array of the message, after it has been encrypted (if a key is set), and size is appended to the front.
        Args:
            message:

        Returns:

        """
        data_bytes = orjson.dumps(message)
        # encrypt if key is available
        if self.fernetInstance and encrypt:
            data_bytes = self.fernetInstance.encrypt(data_bytes)
        data_bytes = struct.pack(">I", len(data_bytes)) + data_bytes
        return data_bytes

    def receive_size(self):
        """
        Receives the size of the message from the socket. The size is appended to the front of the message, and unecrypted.
        Returns: the size of the message.
        """
        size = self.recv_exact(4, False) # do not decrypt size
        size = struct.unpack(">I", size[0])[0]
        return size

    def recv_appended_stream(self, decrypt=True):
        try:
            size = self.receive_size()
            res = self.recv_exact(size, decrypt)
        except (ConnectionError, struct.error, OSError):
            return -1, -1, -1
        else:
            return size, res[0], res[1]

    def recv_exact(self, bytes : int, decrypt_if_available=False, *args, **kwargs) -> (bytes, bool):
        """
        Received the exact number of bytes specified and decrypts the data using the instance's key, if one is set.
        Args:
            bytes: the number of bytes to receive.
            *args, **kwargs: additional arguments to be passed to the socket.recv() function.

        Returns: the decrypted data, and a boolean specifying whether the data was encrypted.
        """
        received = b''
        receivedC = 0
        while receivedC < bytes:
            received += super().recv(bytes - receivedC, *args, **kwargs)
            if len(received) == 0:
                raise ConnectionResetError("recv_exact failed due to socket closing")
            receivedC += len(received)
        if self.fernetInstance and decrypt_if_available:
            return self.fernetInstance.decrypt(received), True
        else:
            return received, False