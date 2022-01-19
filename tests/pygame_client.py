import time
import d3dshot
import mss

rect = {'top': 0, 'left': 0, 'width': 1280 , 'height': 720}
d = d3dshot.create()
with mss.mss() as sct:
    # The region to capture
    i = 0
    start = time.time()
    frames = 0
    while True:
        if time.time() - start >= 1:
            print('{} frames in {} seconds'.format(frames, time.time() - start))
            start = time.time()
            frames = 0
        img = d.screenshot()
        frames += 1