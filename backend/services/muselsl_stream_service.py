import threading
import time
import asyncio
from process.muse_stream import start_muse_stream, begin_streaming_data, check_signal, get_eeg_buffer, end_muse_stream
from fastapi import WebSocket, WebSocketDisconnect

class MuselslStreamService:
    
    def __init__(self):
        self.muselsl_start_event = threading.Event()
        self.muselsl_stop_event = threading.Event()
        self.muselsl_thread = None

    def start_muselsl_stream(self, mac_address: str):
        self.muselsl_start_event.clear()
        self.muselsl_stop_event.clear()
        self.muselsl_thread = threading.Thread(target=start_muse_stream, args=(mac_address, self.muselsl_start_event, self.muselsl_stop_event))
        self.muselsl_thread.start()

        while not self.muselsl_start_event.is_set() and self.muselsl_thread.is_alive():
            time.sleep(0.1)

        if self.muselsl_start_event.is_set():
            return {"data": "Streaming"}
        return {"data": "No Stream"}

    def end_stream(self):
        self.pylsl_stop_event.set()
        if self.pylsl_thread is not None:
            self.pylsl_thread.join()
        self.muselsl_stop_event.set()
        if self.muselsl_thread is not None:
            self.muselsl_thread.join()
        return {"data": "Pylsl and muselsl terminated"}

