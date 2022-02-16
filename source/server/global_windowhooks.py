import logging
import threading
import MWindowModel
import time

RUNNING = True

def init(model, controller):
    threading.Thread(target=threadCount).start()
    global MODEL
    MODEL = model
    global CONTROLLER
    CONTROLLER = controller


def threadCount():
    # print number of threads running in a loop
    while RUNNING:
        logging.debug("Active Threads: " + str(threading.active_count()))
        time.sleep(1)

def win_close():
    """
    Handles application close request:
    - Stop listener thread.
    - Cancel downloads/uploads.
    - Close screen sharing.
    """
    MWindowModel.LISTENER_RUNNING = False
    for client in MWindowModel.clients.values():
        client.close()
    for controller in CONTROLLER.inspected_clients.values():
        controller.fileExplorerManager.stop_downloads()
        controller.close()
    global RUNNING
    RUNNING = False
    print("----------------- APPLICATION CLOSE EVENT FINISHED -----------------")