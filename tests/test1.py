import time

import numpy as np
import cv2
from mss import mss
from PIL import Image

bounding_box = {'top': 0, 'left': 0, 'width': 1, 'height': 1}

sct = mss()

while True:
    start = time.time()
    sct_img = sct.grab(bounding_box)
    print(1/(time.time()-start))
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
        cv2.destroyAllWindows()
        break