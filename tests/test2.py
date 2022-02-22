# import time
# import cv2
# import mss
# import mss.windows
# import numpy
# from turbojpeg import TurboJPEG
#
# jpeg = TurboJPEG()
# mss.windows.CAPTUREBLT = 0
#
#
# def bl():
#     with mss.mss() as sct:
#         monitor = sct.monitors[0]
#
#         # Part of the screen to capture
#         monitor = {'top': 40, 'left': 0, 'width': 800, 'height': 640}
#
#         while 'Screen capturing':
#             last_time = time.time()
#
#             # Get raw pixels from the screen, save it to a Numpy array
#             img = numpy.array(sct.grab(monitor))
#
#             # Display the picture
#             cv2.imshow('OpenCV/Numpy normal', img)
#
#             image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
#             image = jpeg.encode(image, quality=75)
#
#             # Display the picture in grayscale
#             # cv2.imshow('OpenCV/Numpy grayscale',
#             # cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))
#
#             print('fps: {0}'.format(1 / (time.time()-last_time)))
#
#             # Press "q" to quit
#             if cv2.waitKey(25) & 0xFF == ord('q'):
#                 cv2.destroyAllWindows()
#                 break
# bl()
import configparser

c = configparser.ConfigParser()
c.read_file(open('runconfig.ini'))
d = c['CONNECTION']['ip']
print(d)