import io
from socket import socket
from threading import Thread
# from zlib import compress
# import time
# import mss
# from PIL import Image
#
# def retrieve_screenshot(conn):
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
#             #Send the size of the pixels length
#
#             # Send pixels
#             buffer.seek(0)
#             g = buffer.read()
#             conn.send(len(g).to_bytes(4, "big"))
#             conn.send(g)
#
#
# def main(host='127.0.0.1', port=5202):
#     sock = socket()
#     sock.connect((host, port))
#     thread = Thread(target=retrieve_screenshot, args=(sock,))
#     thread.start()
#     thread.join()
#
#
# if __name__ == '__main__':
#     main()
#
import io
from socket import socket
from threading import Thread
from zlib import compress
import time
import mss
from PIL import Image

def retrieve_screenshot(conn):
    rect = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
    with mss.mss() as sct:
        # The region to capture
        i = 0
        start = time.time()
        while True:
            if i == 30:
                print('30 frames in {} seconds'.format(time.time() - start))
                i = 0
                start = time.time()
            i += 1
            image = sct.grab(rect)
            g = compress(image.rgb)
            conn.send(len(g).to_bytes(4, "big"))
            conn.send(g)


def main(host='192.168.1.157', port=5202):
    sock = socket()
    sock.connect((host, port))
    thread = Thread(target=retrieve_screenshot, args=(sock,))
    thread.start()
    thread.join()


if __name__ == '__main__':
    main()
