from zlib import decompress
import pygame
import socket
from io import BytesIO
from PIL import Image
from NetProtocol import *
import OpenConnectionHelpers

keys = {name : value for value, name in vars(pygame.constants).items() if type(name) == int and value.startswith('K_')}

def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def main(client):
    conn = OpenConnectionHelpers.open_connection(client)
    conn.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetRemoteControl)))
    size, data = NetProtocol.unpackFromSocket(conn)
    response = orjson.loads(data)
    if response['type'] == NetTypes.NetStatus.value:
        if response['data'] == NetStatusTypes.NetOK.value:
            pygame.init()
            window  = pygame.display.set_mode((1920, 1080))
            clock = pygame.time.Clock()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        print(f"Key pressed: {keys[event.key]}")
                        client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetKeyboardAction, extra=keys[event.key][2:]))
                size = conn.recv(4)
                size = int.from_bytes(size, byteorder='big')
                pixels = recvall(conn, size)
                im = Image.open(BytesIO(pixels))
                img = pygame.image.fromstring(im.tobytes(), (1920, 1080), 'RGB')
                img = pygame.transform.scale(img, (1920, 1080))
                window.blit(img, (0, 0))
                pygame.display.flip()