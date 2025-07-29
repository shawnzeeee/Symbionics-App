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
            # self.record_data_event.clear()
            # self.pylsl_thread = threading.Thread(target=begin_streaming_data, args=(self.pylsl_stop_event, self.record_data_event))
            # self.pylsl_thread.start()
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

    async def check_signal(self, websocket: WebSocket):
        if self.muselsl_thread and self.muselsl_thread.is_alive() and self.pylsl_thread and self.pylsl_thread.is_alive():
            await websocket.accept()
            try:
                while True:
                    eeg_buffer = get_eeg_buffer()
                    signal_quality = check_signal(eeg_buffer)
                    await websocket.send_json(signal_quality)
                    await asyncio.sleep(1)
            except WebSocketDisconnect:
                print("WebSocket disconnected")
        else:
            await websocket.close()
