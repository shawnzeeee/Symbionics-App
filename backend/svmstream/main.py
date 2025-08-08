from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import threading
import asyncio
from backend.routers import svm  # <- import the websocket router


app = FastAPI()

tasks = {}

from muse_stream import start_muse_stream, update_eeg_buffer
from test import classify
from calibration import calibrate
from test import get_attention_threshold

import time

muselsl_start_event = threading.Event()
muselsl_stop_event = threading.Event()
pylsl_stop_event = threading.Event()
pylsl_start_event = threading.Event()
calibration_thread = threading.Event()

classifier_thread = None
pylsl_thread = None
muselsl_thread = None
blink_collection_thread = None

start_calibration = True
def connect_muse(mac_address: str,filename):
    global muselsl_thread, muselsl_start_event, muselsl_stop_event, pylsl_thread, pylsl_stop_event
    pylsl_start_event.clear()
    pylsl_stop_event.clear()
    muselsl_start_event.clear()
    muselsl_stop_event.clear()
    muselsl_thread = threading.Thread(target=start_muse_stream, args=(mac_address, muselsl_start_event, muselsl_stop_event))
    muselsl_thread.start()

    while not muselsl_start_event.is_set() and muselsl_thread.is_alive():
        time.sleep(0.1)

    if muselsl_start_event.is_set():
        pylsl_thread = threading.Thread(target=update_eeg_buffer, args=(pylsl_start_event, pylsl_stop_event))
        pylsl_thread.start()
        while not pylsl_start_event.is_set() and pylsl_thread.is_alive():
            time.sleep(0.1)

        # if start_calibration:
        #     calibration_thread = threading.Thread(target=calibrate, args=(muselsl_stop_event,))
            # calibration_thread.start()
        if pylsl_start_event.is_set():
            classifier_thread = threading.Thread(target=classify, args=(muselsl_stop_event,filename))
            classifier_thread.start()
    return {"data" : "Stream Stopped"}

def disconnect_muse():
    global muselsl_thread, muselsl_stop_event, pylsl_stop_event
    pylsl_stop_event.set()
    if pylsl_thread is not None:
        pylsl_thread.join()  # Wait for the thread to terminate
    muselsl_stop_event.set()
    if muselsl_thread is not None:
        muselsl_thread.join()
    return {"data": "Pylsl and muselsl terminated"}

# Include the websocket router
app.include_router(svm)

def main(filename):
    try:
        response = connect_muse('00:55:DA:B0:1E:78',filename=filename)
        WebSocket.send(get_attention_threshold())
        print(response)
    except Exception as e:
        print(e)
if __name__ == "__main__":
    main()