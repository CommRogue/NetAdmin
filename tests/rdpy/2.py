from zlib import decompress
import pygame
import socket

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
        size = conn.recv(4)
        size = int.from_bytes(size, byteorder='big')
        pixels = recvall(conn, size)
        img = pygame.image.fromstring(pixels, (1920, 1080), 'RGB')
        window.blit(img, (0, 0))
        pygame.display.flip()
main()