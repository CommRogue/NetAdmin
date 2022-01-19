from zlib import decompress
import pygame
import socket
from io import BytesIO
from PIL import Image

def recvall(conn, length):
    """ Retreive all pixels. """

    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))
        if not data:
            return data
        buf += data
    return buf

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 5202))
    s.listen(5)
    conn, addr = s.accept()
    pygame.init()
    window  = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        size = conn.recv(4)
        size = int.from_bytes(size, byteorder='big')
        pixels = recvall(conn, size)
        im = Image.open(BytesIO(pixels))
        img = pygame.image.fromstring(im.tobytes(), (1920, 1080), 'RGB')
        img = pygame.transform.scale(img, (1920, 1080))
        window.blit(img, (0, 0))
        pygame.display.flip()
main()