import ast
import ctypes
import queue
import threading
import pygame
import pyperclip

import SmartSocket
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

def handleReceive(queue, conn : SmartSocket.SmartSocket, remote_resolution):
    i = 0
    cSumData = 0
    while True:
        if i == 60:
            logging.info(f"[SCREENSHARE] 60 FPS in {cSumData/1000000}MB")
            cSumData = 0
            i = 0
        size, pixels, isEncrypted = conn.recv_appended_stream()
        if pixels == -1:
            break
        # print("FRAME ENCRYPTION STATUS:", isEncrypted)
        cSumData += size
        # TODO - Debug cause of premature JPEG?
        # check if pixels end in \xff\xd9 (end of jpeg)
        if pixels[-2:] == b"\xff\xd9":
            pixels = jpeg.decode(pixels)
            img = pygame.image.frombuffer(pixels, remote_resolution, 'RGB')
            queue.put(img)
            i += 1
        else:
            logging.info("[SCREENSHARE] PREMATURE JPEG DETECTED")


def main(client):
    # request open connection
    conn = OpenConnectionHelpers.open_connection(client, encrypt=False)
    # send pygame_resolution to tell client capture size
    conn.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetRemoteControl))
    # load response
    size, response, isEncrypted = conn.receive_message()

    if response['type'] == NetTypes.NetStatus.value:
        if response['data'] == NetStatusTypes.NetOK.value:
            # calculate local resolution
            user32 = ctypes.windll.user32
            local_resolution = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
            remote_resolution = ast.literal_eval(response['extra'])
            pygame_resolution = (min(local_resolution[0]/1.1, remote_resolution[0]), min(local_resolution[1]/1.1, remote_resolution[1]))
            x_diff_multiplier = (remote_resolution[0]/pygame_resolution[0])
            y_diff_multiplier = (remote_resolution[1]/pygame_resolution[1])
            pygame.init()
            window = pygame.display.set_mode(pygame_resolution, flags=pygame.RESIZABLE)
            imgqueue = queue.Queue()
            event_thread = threading.Thread(target=handleReceive, args=(imgqueue, conn, remote_resolution,))
            event_thread.start()
            clock = pygame.time.Clock()
            try:
                while True:
                    # check if queue is empty
                    if not imgqueue.empty():
                        img = imgqueue.get_nowait()
                        img = pygame.transform.smoothscale(img, pygame_resolution)
                        window.blit(img, (0, 0))
                        pygame.display.flip()
                    # handle input
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            conn.close()
                            return
                        if event.type == pygame.KEYDOWN:
                            print(f"Key pressed: {keys[event.key]}")
                            if keys[event.key] != "K_ESCAPE":
                                if (keys[event.key] == "K_v" or keys[event.key] == "K_V") and pygame.key.get_mods() & pygame.KMOD_CTRL: # paste
                                    client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetPasteText, extra=pyperclip.paste()))
                                elif (keys[event.key] == "K_c" or keys[event.key] == "K_C") and pygame.key.get_mods() & pygame.KMOD_CTRL: # copy
                                    client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetCopyText))
                                else:
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
                            pg_mouse_pos = pygame.mouse.get_pos()
                            # multiply by localres -> remoteres multiplier
                            mouse_pos = (round(pg_mouse_pos[0] * x_diff_multiplier, 1),
                                         round(pg_mouse_pos[1] * y_diff_multiplier, 1))
                            client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickDownAction,
                                                           extra=(event.button, *mouse_pos)))
                        if event.type == pygame.MOUSEBUTTONUP:
                            pg_mouse_pos = pygame.mouse.get_pos()
                            # multiply by localres -> remoteres multiplier
                            mouse_pos = (round(pg_mouse_pos[0] * x_diff_multiplier, 1),
                                         round(pg_mouse_pos[1] * y_diff_multiplier, 1))
                            client.send_message(NetMessage(type=NetTypes.NetRequest, data=NetTypes.NetMouseClickUpAction,
                                                           extra=(event.button, *mouse_pos)))
                        if event.type == pygame.VIDEORESIZE:
                            pygame_resolution = (event.w, event.h)
                            x_diff_multiplier = (remote_resolution[0] / pygame_resolution[0])
                            y_diff_multiplier = (remote_resolution[1] / pygame_resolution[1])

                    clock.tick(60)
                    # size = conn.recv(4)
                    # size = int.from_bytes(size, byteorder='big')
                    # pixels = recvall(conn, size)
                    # pixels = jpeg.decode(pixels)
                    # img = pygame.image.frombuffer(pixels, remote_resolution, 'RGB')
                    # img = pygame.transform.scale(img, pygame_resolution)
                    # window.blit(img, (0, 0))
                    # pygame.display.flip()
            except Exception as e:
                print(e)
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