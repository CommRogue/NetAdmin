import ast
import ctypes
import queue
import threading
from zlib import decompress
import pygame
import socket
from io import BytesIO
from PIL import Image
from NetProtocol import *
import OpenConnectionHelpers
from turbojpeg import TurboJPEG

jpeg = TurboJPEG()

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

# def handleReceive(queue, conn):
#     while True:
#         try:
#             size = conn.recv(4)
#             size = int.from_bytes(size, byteorder='big')
#             pixels = recvall(conn, size)
#             pixels = jpeg.decode(pixels)
#             img = pygame.image.frombuffer(pixels, (1920, 1080), 'RGB')
#             img = pygame.transform.scale(img, (1920, 1080))
#             queue.put(img)
#         except:
#             return

def main(client):
    conn = OpenConnectionHelpers.open_connection(client)
    conn.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetRemoteControl)))
    size, data = NetProtocol.unpackFromSocket(conn)
    response = orjson.loads(data)
    if response['type'] == NetTypes.NetStatus.value:
        if response['data'] == NetStatusTypes.NetOK.value:
            remote_resolution = ast.literal_eval(response['extra'])
            user32 = ctypes.windll.user32
            local_resolution = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
            half_local_res = (int(local_resolution[0]/1.5), int(local_resolution[1]/1.5))
            x_diff_multiplier = (remote_resolution[0]/half_local_res[0])
            y_diff_multiplier = (remote_resolution[1]/half_local_res[1])
            pygame.init()
            window  = pygame.display.set_mode(half_local_res)
            # imgqueue = queue.Queue()
            # event_thread = threading.Thread(target=handleReceive, args=(imgqueue, conn))
            # event_thread.start()
            try:
                while True:
                    # # check if queue is empty
                    # if not imgqueue.empty():
                    #     window.blit(imgqueue.get_nowait(), (0, 0))
                    #     pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            conn.close()
                            return
                        if event.type == pygame.KEYDOWN:
                            print(f"Key pressed: {keys[event.key]}")
                            client.send_message(
                                NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetKeyboardAction,
                                           extra=keys[event.key][2:]))
                        if event.type == pygame.MOUSEMOTION:
                            pg_mouse_pos = pygame.mouse.get_pos()
                            # multiply by localres -> remoteres multiplier
                            mouse_pos = (round(pg_mouse_pos[0] * x_diff_multiplier, 1), round(pg_mouse_pos[1] * y_diff_multiplier, 1))
                            client.send_message(
                                NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseMoveAction, extra=mouse_pos))
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickDownAction,
                                                           extra=(event.button, mouse_pos[0], mouse_pos[1])))
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouse_pos = pygame.mouse.get_pos()
                            client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickUpAction,
                                                           extra=(event.button, mouse_pos[0], mouse_pos[1])))
                    size = conn.recv(4)
                    size = int.from_bytes(size, byteorder='big')
                    pixels = recvall(conn, size)
                    pixels = jpeg.decode(pixels)
                    img = pygame.image.frombuffer(pixels, remote_resolution, 'RGB')
                    img = pygame.transform.scale(img, half_local_res)
                    window.blit(img, (0, 0))
                    pygame.display.flip()
            except:
                pygame.quit()
                try:
                    conn.close()
                except:
                    pass
                return
# def main(client):
#     conn = OpenConnectionHelpers.open_connection(client)
#     conn.send(NetProtocol.packNetMessage(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetRemoteControl)))
#     size, data = NetProtocol.unpackFromSocket(conn)
#     response = orjson.loads(data)
#     if response['type'] == NetTypes.NetStatus.value:
#         if response['data'] == NetStatusTypes.NetOK.value:
#             pygame.init()
#             window  = pygame.display.set_mode((1920, 1080))
#             clock = pygame.time.Clock()
#             while True:
#                 for event in pygame.event.get():
#                     if event.type == pygame.QUIT:
#                         pygame.quit()
#                         return
#                     if event.type == pygame.KEYDOWN:
#                         print(f"Key pressed: {keys[event.key]}")
#                         client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetKeyboardAction, extra=keys[event.key][2:]))
#                     if event.type == pygame.MOUSEMOTION:
#                         mouse_pos = pygame.mouse.get_pos()
#                         client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseMoveAction, extra=mouse_pos))
#                     if event.type == pygame.MOUSEBUTTONDOWN:
#                         mouse_pos = pygame.mouse.get_pos()
#                         client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickDownAction, extra=(event.button, mouse_pos[0], mouse_pos[1])))
#                     if event.type == pygame.MOUSEBUTTONUP:
#                         mouse_pos = pygame.mouse.get_pos()
#                         client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickUpAction, extra=(event.button, mouse_pos[0], mouse_pos[1])))
#                 size = conn.recv(4)
#                 size = int.from_bytes(size, byteorder='big')
#                 pixels = recvall(conn, size)
#                 im = Image.open(BytesIO(pixels))
#                 img = pygame.image.fromstring(im.tobytes(), (1920, 1080), 'RGB')
#                 img = pygame.transform.scale(img, (1920, 1080))
#                 window.blit(img, (0, 0))
#                 pygame.display.flip()