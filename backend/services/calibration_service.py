import threading
from process.calibration import calibrate
from process.muse_stream import begin_streaming_data, check_signal, end_muse_stream
from services.muselsl_stream_service import MuselslStreamService
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

    # function to append "Calnum", then adder and subtractor to CSV for calibration purposes
    def updateCSV(self, filename, adder, subtractor):
        # Build the path in the SavedData folder
        if not filename.endswith(".csv"):
            filename = filename + ".csv"
        save_dir = os.path.join(os.getcwd(), "SavedData")
        os.makedirs(save_dir, exist_ok=True)
        csv_path = os.path.join(save_dir, filename)
        print(csv_path)

        # Load the CSV
        df = pd.read_csv(csv_path)
        
        # If column 6 doesn't exist yet, create it
        if len(df.columns) < 6:
            df['CalNum'] = ""
        
        # Set first three rows
        df.iloc[0, 5] = adder
        df.iloc[1, 5] = subtractor
        
        # Save back to CSV
        df.to_csv(csv_path, index=False)
        return True


    #for gathering eeg data, writing to a csv file
    def begin_pylsl_stream(self, file_name):
        # Build the path in the SavedData folder
        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"
        save_dir = os.path.join(os.getcwd(), "SavedData")
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, file_name)
        print(file_path)

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
    
    #for calibrate model, where we don't need to write to a file
    def begin_pylsl_stream_no_file_write(self, file_name):
        # Build the path in the SavedData folder
        if not file_name.endswith(".csv"):
            file_name = file_name + ".csv"
        file_name = "test_data.csv"
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
    
    def end_muse_pylsl_stream(self):
        #stop pylsl thread
        self.pylsl_stop_event.set()
        if self.pylsl_thread is not None:
            self.pylsl_thread.join()

        #stop muselsl thread
        end_muse_stream()
        return {"data": "muselsl, pylsl thread ended"}

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
    
    def fetch_sensitivity_values(self, filename):
        if not filename.endswith(".csv"):
            filename += ".csv"
        save_dir = os.path.join(os.getcwd(), "SavedData")
        csv_path = os.path.join(save_dir, filename)
        df = pd.read_csv(csv_path)
        if 'CalNum' not in df.columns:
            print("CalNum column does not exist in the CSV file.")
            return {"error": "CalNum column not found"}
        calnum_column = df['CalNum']
        output = {
            "data": {
                "attention_adder": calnum_column[0],
                "attention_subtractor": calnum_column[1]
            }
        }
        print(output)
        return output  
    
    async def begin_checking_attention_threshold(self, websocket):
        if self.pylsl_thread == None:
            print("No pylsl thread")
            return {"data": "No pylsl thread"}
        while not self.pylsl_start_event.is_set() and self.pylsl_thread.is_alive():
            #time.sleep(0.1)
            await asyncio.sleep(0.1)   # <-- was time.sleep


        if self.pylsl_start_event.is_set():
            await classifier_process.classifier_loop(websocket, self.pylsl_stop_event)
    
    async def set_attention_adjustments(self, adder=None, subtractor=None):
        return classifier_process.set_attention_adjustments(adder, subtractor)

    async def get_attention_adjustments(self):
        return classifier_process.get_attention_adjustments()
    
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