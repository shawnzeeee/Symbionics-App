import threading
from process.calibration import calibrate
from process.muse_stream import begin_streaming_data, check_signal
from services.muselsl_stream_service import MuselslStreamService
import csv
import time
import os
import asyncio

from sklearn.svm import SVC
import pandas as pd
from .shared_instances import classifier_process
class CalibrationService:
    def __init__(self, stream_service: MuselslStreamService):
        self.calibration_thread = None
        self.pylsl_thread = None
        self.check_signal_thread = None
        self.pylsl_start_event = threading.Event()
        self.pylsl_stop_event = threading.Event()
        self.record_data_event = threading.Event()
        self.stream_service = stream_service

    def begin_pylsl_stream(self, file_name):
        # Build the path in the SavedData folder
        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"

        save_dir = os.path.join(os.getcwd(), "SavedData")
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        muselsl_thread = self.stream_service.muselsl_thread
        muselsl_start_event = self.stream_service.muselsl_start_event
        if muselsl_thread == None:
            print("Muselsl not running")
            return {"data": "Muselsl not running"}
        
        if muselsl_thread.is_alive() and muselsl_start_event.is_set():
            self.pylsl_start_event.clear()
            self.pylsl_stop_event.clear()
            self.record_data_event.clear()
            self.pylsl_thread = threading.Thread(target=begin_streaming_data, args=(file_path,self.pylsl_start_event, self.pylsl_stop_event, self.record_data_event))
            self.pylsl_thread.start()

            while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
                time.sleep(0.1)
            return {"data": "Succesfully start pylsl stream"}
        
        return {"data": "There was error connecting to muselsl stream"}
    
    def begin_calibration(self):
        muselsl_thread = self.stream_service.muselsl_thread
        muselsl_start_event = self.stream_service.muselsl_start_event
        if muselsl_thread.is_alive() and muselsl_start_event.is_set() and self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():       
            calibrate(self.record_data_event)

        # self.disconnect_muse()
        self.pylsl_stop_event.set()
        return {"data":"Succesfully calibrated"}

    async def begin_checking_signal(self, websocket):
        # Build the path in the SavedData folder
        if self.pylsl_thread == None:
            print("No pylsl thread")
            return {"data": "No pylsl thread"}

        while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
            # time.sleep(0.1)
            await asyncio.sleep(0.1)   # <-- was time.sleep


        if self.pylsl_start_event.is_set():
            await check_signal(websocket, self.pylsl_stop_event)
        return {"data": "Succesfully calibrated"}
    
    def train_classifier(self, filename):
        response = classifier_process.train_classifier(filename)
        return {"data": response}
    
    async def begin_checking_attention_threshold(self, websocket):
        if self.pylsl_thread == None:
            print("No pylsl thread")
            return {"data": "No pylsl thread"}
        while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
            #time.sleep(0.1)
            await asyncio.sleep(0.1)   # <-- was time.sleep


        if self.pylsl_start_event.is_set():
            await classifier_process.classifier_loop(websocket, self.pylsl_stop_event)
    
    def disconnect_muse(self):
        muselsl_thread = self.stream_service.muselsl_thread
        muselsl_start_event = self.stream_service.muselsl_start_event
        muselsl_stop_event = self.stream_service.muselsl_stop_event

        self.pylsl_stop_event.set()
        if self.pylsl_thread is not None:
            self.pylsl_thread.join()  # Wait for the thread to terminate
        muselsl_stop_event.set()
        if muselsl_thread is not None:
            muselsl_thread.join()
        print("Pylsl and muselsl terminated")
        return {"data": "Pylsl and muselsl terminated"}

# calibration_service.py (module scope, not inside the class!)
import asyncio

# Shared adjustment state (defaults)
_adjust = {"adder": 15, "subtractor": 15}
_adjust_lock = asyncio.Lock()

def _clamp(v, lo=0, hi=220):
    try:
        v = int(v)
    except Exception:
        return lo
    return max(lo, min(hi, v))

async def set_attention_adjustments(adder=None, subtractor=None):
    async with _adjust_lock:
        if adder is not None:
            _adjust["adder"] = _clamp(adder)
        if subtractor is not None:
            _adjust["subtractor"] = _clamp(subtractor)

async def get_attention_adjustments():
    async with _adjust_lock:
        return _adjust["adder"], _adjust["subtractor"]

def apply_attention_adjustments(base_value: float, lo=0, hi=220) -> int:
    """Fast read—OK without lock since we’re just reading ints."""
    a = _adjust["adder"]
    s = _adjust["subtractor"]
    return _clamp(int(base_value) + a - s, lo, hi)
