from SmartSocket import SmartSocket
import time
from NetProtocol import NetTypes, NetMessage, NetStatusTypes
import numpy
import mss
from turbojpeg import TurboJPEG
import cv2

#@profile
def screenShareClient(conn : SmartSocket, response_id, jpeg : TurboJPEG) -> None:
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        # send response to client
        # user32 = ctypes.windll.user32
        # local_resolution = str((user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)))
        local_resolution = (monitor['width'], monitor['height'])
        conn.send_message(
            NetMessage(type=NetTypes.NetStatus, data=NetStatusTypes.NetOK, extra=str(local_resolution), id=response_id))

        # The region to capture
        i = 0
        start = time.time()
        while True:
            if i == 30:
                print(f'ScreenShare FPS: {(30 / (time.time() - start))}')
                i = 0
                start = time.time()
            i += 1
            image = numpy.array(sct.grab(monitor))
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = jpeg.encode(image, quality=75)
            # buffer = io.BytesIO()
            # im = Image.frombytes('RGB', image.size, image.rgb)
            # im.save(buffer, format="JPEG", quality=75)
            # Send the size of the pixels length

            # # Send pixels
            # buffer.seek(0)
            # g = buffer.read()
            # conn.send(len(image).to_bytes(4, "big"))
            # conn.send(image)
            try:
                conn.send_appended_stream(image)
            except:
                print("ScreenShare connection closed")
                return