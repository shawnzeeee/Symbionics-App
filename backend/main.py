from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import BackgroundTasks
import re
import threading


tasks = {}

app = FastAPI()

# Allow requests from your frontend (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for all origins (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def read_root():
    return {"message": "Hello from FastAPI!"}

from muse_stream import get_devices_list
@app.get("/api/devices")
def read_root():
    response = get_devices_list()
    #lines = response.strip().splitlines()
    devices = []
    devices = response
    print(devices)
    return {"data": devices}

from muse_stream import start_muse_stream, update_eeg_buffer
pylsl_stop_event = threading.Event()
muselsl_start_event = threading.Event()
muselsl_stop_event = threading.Event()
pylsl_thread = None
muselsl_thread = None
@app.get("/api/start-stream")
def connect_muse(mac_address: str):
    global muselsl_thread, muselsl_start_event, muselsl_stop_event, pylsl_thread, pylsl_stop_event
    pylsl_stop_event.clear()
    muselsl_stop_event.clear()
    #start_muse_stream(mac_address, muselsl_stop_event)
    muselsl_thread = threading.Thread(target=start_muse_stream, args=(mac_address, muselsl_start_event, muselsl_stop_event))
    #pylsl_thread = threading.Thread(target=update_eeg_buffer, args=(stop_event,))
    #pylsl_thread.start()
    return {"data" : "Stream Stopped"}


from muse_stream import end_muse_stream
@app.get("/api/end-stream")
def disconnect_muse():
    global pylsl_stop_event
    pylsl_stop_event.set()
    #if pylsl_thread is not None:
        #pylsl_thread.join()  # Wait for the thread to terminate
    response = end_muse_stream()
    return {"data": response}

