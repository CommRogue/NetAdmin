# from socket import socket
# from threading import Thread
# from zlib import compress
# import time
# import mss
# from PIL import Image
#
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
#             img = sct.grab(rect).rgb
#             #Send the size of the pixels length
#             conn.send(len(img).to_bytes(4, "big"))
#
#             # Send pixels
#             conn.sendall(img)
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
import zlib
import mss
import time
from PIL import Image
import io
rect = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

with mss.mss() as sct:
    b = sct.grab(rect)
    print(len(b.rgb))
    start = time.time()
    buffer = io.BytesIO()
    im = Image.frombytes('RGB', b.size, b.bgra, 'raw', 'BGRX')
    im.save(buffer, format='JPEG', quality=75)
    print(f"Took {time.time() - start} seconds")
    print(buffer.getbuffer().nbytes)
    im2 = Image.open(buffer)
    im2.show()