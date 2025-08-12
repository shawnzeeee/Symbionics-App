import time
from sklearn.svm import SVC
import os
import pandas as pd
import asyncio, json, numpy as np

from .feature_extraction import *
from .filter import *

from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from .muse_stream import get_eeg_buffer
import asyncio
class ClassifierProcess:
    def __init__(self):
        self.window_size = 500
        self.num_windows = 5
        self.filter_funcs = [bandpass_filter, clean_eeg_ica_threshold]
        self.feature_funcs = [calculate_hjorth_parameters, calculate_bandpowers, calculate_log_variance]

        self.classifier = SVC(kernel='linear', probability=True)
        self.scaler = StandardScaler()
    def extract_feature_vector(self,indices, df, window_size, classification, num_windows=5, filter_funcs=[], feature_funcs=[]):
        processed_data = []
        for start_idx in indices:
            for w in range(num_windows):
                window_start = start_idx + w * window_size
                window_end = window_start + window_size
                if window_end > len(df):
                    continue
                window = df.iloc[window_start:window_end, :4].values
                #print(window.shape)

                for func in filter_funcs:
                    window = func(window)
                
                features = []
                for i in range(4):
                    signal = window[:,i]
                    for func in feature_funcs:
                        input = func(signal)
                        if hasattr(input, '__iter__') and not isinstance(input, str):
                            features.extend(input)
                        else:
                            features.append(input)
                #actual_class = df.iloc[window_start, 4]
                features.append(classification)
                processed_data.append(features)
        return processed_data

    def train_classifier(self,filename):
        save_dir = os.path.join(os.getcwd(), "SavedData")
        file_path = os.path.join(save_dir, filename)
        if not os.path.exists(file_path):
            return "File Not Found"
        # Load the CSV as a DataFrame
        df = pd.read_csv(file_path)
        # print("CSV columns:", list(df.columns))
        attention_indices = df.index[df['Class'] == 2].tolist()
        idle_indices = df.index[df['Class'] == 1].tolist()

        Xy = []
        Xy.extend(self.extract_feature_vector(attention_indices, df, self.window_size, 2, self.num_windows, self.filter_funcs, self.feature_funcs))
        Xy.extend(self.extract_feature_vector(idle_indices, df, self.window_size, 1, self.num_windows, self.filter_funcs, self.feature_funcs))
        Xy = pd.DataFrame(Xy).values
        X = Xy[:, :-1]
        y = Xy[:, -1]

        X_scaled = self.scaler.fit_transform(X)
        self.classifier.fit(X_scaled,y)
        return "Classifier succesfully trained"

    async def classifier_loop(self, websocket, stop_event):
        try:
            attention_threshold = 0
            attention_adder = 15
            attention_subtractor = 15

            while not stop_event.is_set():
                #pull a window
                data_array = get_eeg_buffer()
                #data_array = np.zeros(window_size*4, dtype=np.float32)
                if len(data_array) < self.window_size:
                    await asyncio.sleep(0.05)
                    continue
                if len(data_array) == self.window_size*4:
                    eeg_window = data_array.reshape(self.window_size, 4)
                    features = []
                    for func in self.filter_funcs:
                        eeg_window = func(eeg_window)
                    for ch in range(4):
                        signal = eeg_window[:, ch]
                        for func in self.feature_funcs:
                            input = func(signal)
                            if hasattr(input, '__iter__') and not isinstance(input, str):
                                features.extend(input)
                            else:
                                features.append(input)
                    
                    features = np.array(features).reshape(1, -1)
                    if not np.isfinite(features).all():
                        print("NANANANANANANNANANAN")
                        continue
                    features_scaled = self.scaler.transform(features)

                    predicted_class = self.classifier.predict(features_scaled)[0]
                    
                    # try:
                    #     data = await asyncio.wait_for(websocket.receive_json(), timeout=0.01)
                    #     attention_subtractor = data.get("attention_subtractor", attention_subtractor)
                    #     attention_adder = data.get("attention_adder", attention_adder)
                    # except asyncio.TimeoutError:
                    #     pass  # No new message, just continue
                    adder = -1 * attention_subtractor
                    if predicted_class == 2:
                        adder = attention_adder

                    attention_threshold += adder
                    attention_threshold = max(0, min(attention_threshold, 220))
                    gesture = 'O'
                    if attention_threshold >= 100:
                        gesture = 'C'

                    await websocket.send_json({
                        "gesture": gesture,
                        "attention_threshold": attention_threshold,
                        "attention_subtractor -": attention_subtractor,
                        "attention_adder": attention_adder
                    })
                
                    #print(f"Predicted class: {gesture}      {attention_threshold}")  
                    await asyncio.sleep(0.05)  # pacing
                    #time.sleep(0.1)      
            print("Exiting classification")
            return
        except KeyboardInterrupt:
            print("Exiting...")