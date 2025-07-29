import threading
from process.calibration import calibrate
from process.muse_stream import begin_streaming_data
from backend.services.muselsl_stream_service import MuselslStreamService
import csv
import time
import os
class CalibrationService:
    def __init__(self, stream_service: MuselslStreamService):
        self.calibration_thread = None
        self.pylsl_thread = None
        self.pylsl_start_event = threading.Event()
        self.pylsl_stop_event = threading.Event()
        self.record_data_event = threading.Event()
        self.stream_service = stream_service

    def begin_calibration(self, file_name: str):
        # Build the path in the SavedData folder
        save_dir = os.path.join(os.getcwd(), "SavedData")
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)

        muselsl_thread = self.stream_service.muselsl_thread
        muselsl_start_event = self.stream_service.muselsl_start_event
        

        if muselsl_thread.is_alive() and muselsl_start_event.is_set():
            with open(file_name, mode='w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Classification"])

                self.record_data_event.clear()
                self.pylsl_start_event.clear()
                self.pylsl_stop_event.clear()
                
                self.pylsl_thread = threading.Thread(target=begin_streaming_data, args=(writer,self.pylsl_start_event, self.pylsl_stop_event, self.record_data_event))
                self.pylsl_thread.start()

                while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
                    time.sleep(0.1)
                
                self.calibration_thread = threading.Thread(target=calibrate, args=(self.record_data_event))
                self.calibration_thread.start()
                self.calibration_thread.join()

                self.pylsl_stop_event.set()
                self.pylsl_thread.join()
        

        

        return {"data": "Succesfully calibrated"}
