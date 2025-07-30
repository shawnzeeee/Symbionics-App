import threading
from process.calibration import calibrate
from process.muse_stream import begin_streaming_data, check_signal
from services.muselsl_stream_service import MuselslStreamService
import csv
import time
import os
import asyncio

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
            with open(file_path, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Classification"])
                self.pylsl_start_event.clear()
                self.pylsl_stop_event.clear()
                self.record_data_event.clear()
                self.pylsl_thread = threading.Thread(target=begin_streaming_data, args=(writer,self.pylsl_start_event, self.pylsl_stop_event, self.record_data_event))
                self.pylsl_thread.start()

                while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
                    time.sleep(0.1)
            return {"data": "Succesfully start pylsl stream"}
        
        return {"data": "There was error connecting to muselsl stream"}
    
    def begin_calibration(self):
        muselsl_thread = self.stream_service.muselsl_thread
        muselsl_start_event = self.stream_service.muselsl_start_event
        if muselsl_thread.is_alive() and muselsl_start_event.is_set() and self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():       
            # self.calibration_thread = threading.Thread(target=calibrate, args=(self.record_data_event))
            # self.calibration_thread.start()
            # self.calibration_thread.join()
            calibrate(self.record_data_event)

        self.disconnect_muse()

    async def begin_checking_signal(self, websocket):
        # Build the path in the SavedData folder
        if self.pylsl_thread == None:
            print("No pylsl thread")
            return {"data": "No pylsl thread"}

        while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
            time.sleep(0.1)

        if self.pylsl_start_event.is_set():
            await check_signal(websocket, self.pylsl_stop_event)
        return {"data": "Succesfully calibrated"}
    
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
