from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import threading
import asyncio


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
import time

muselsl_start_event = threading.Event()
muselsl_stop_event = threading.Event()
pylsl_stop_event = threading.Event()
pylsl_thread = None
muselsl_thread = None
@app.get("/api/start-stream")
def connect_muse(mac_address: str):
    global muselsl_thread, muselsl_start_event, muselsl_stop_event, pylsl_thread, pylsl_stop_event
    pylsl_stop_event.clear()
    muselsl_start_event.clear()
    muselsl_stop_event.clear()
    muselsl_thread = threading.Thread(target=start_muse_stream, args=(mac_address, muselsl_start_event, muselsl_stop_event))
    muselsl_thread.start()

    while not muselsl_start_event.is_set() and muselsl_thread.is_alive():
        time.sleep(0.1)

    if muselsl_start_event.is_set():
        pylsl_thread = threading.Thread(target=update_eeg_buffer, args=(pylsl_stop_event,))
        pylsl_thread.start()

    return {"data" : "Stream Stopped"}

from muse_stream import check_signal, get_eeg_buffer
@app.get("/api/check-signal")
async def check_muse_signal(websocket: WebSocket):
    global muselsl_thread, pylsl_thread
    if muselsl_thread.is_alive() and pylsl_thread.is_alive():
        await websocket.accept()
        try:
            while True:
                eeg_buffer = get_eeg_buffer()
                signal_quality = check_signal(eeg_buffer)
                await websocket.sendn_json(signal_quality)
                asyncio.sleep(1)
        except WebSocketDisconnect:
            print("WebSocket disconnected")

    return {"data": "Could not find stream"}

from muse_stream import end_muse_stream
@app.get("/api/end-stream")
def disconnect_muse():
    global muselsl_thread, muselsl_stop_event, pylsl_stop_event
    pylsl_stop_event.set()
    if pylsl_thread is not None:
        pylsl_thread.join()  # Wait for the thread to terminate
    muselsl_stop_event.set()
    if muselsl_thread is not None:
        muselsl_thread.join()
    return {"data": "Pylsl and muselsl terminated"}

