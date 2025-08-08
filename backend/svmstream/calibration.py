import threading
import pandas as pd
import time

from muse_stream import get_eeg_buffer
from sklearn.svm import SVC
from classifiers import *
from window_extractor import extract_feature_vector, extract_feature_vector_from_window
from feature_extraction import *
from filter import *
gesture_code = 0
gesture_code_lock = threading.Lock()

window_size = 500
filter_funcs = [bandpass_filter, clean_eeg_ica_threshold]
feature_funcs = [calculate_bandpowers, calculate_hjorth_parameters, calculate_log_variance]

def send_gesture_classification(code):
    global gesture_code, gesture_code_lock
    with gesture_code_lock:
        gesture_code = code

def initial_baseline_recording():
    global window_size, filter_funcs, feature_funcs
    #record 10 seconds of data
    samples = []
    for _ in range(10):
        eeg_data = get_eeg_buffer()
        window = eeg_data.reshape(window_size, 4)
        features = extract_feature_vector_from_window(window, 0, filter_funcs, feature_funcs)
        samples.append(features)
        time.sleep(1)
    samples_np = np.array(samples)
    return samples_np

# def initial_active_recording():
#     #feature extraction
#     #measure distance from hypersurface of 1 class SVM
#     #create quality gate to only allow record data points that produces a distance above a threshold
#     #record until data is balanced between active and baseline
    
    
# def baseline_recording():
#     #feature extraction
#     #measure distance from hyperplane of 2 class SVM
#     #create quality gate to only allow record data points that produces a distance above a threshold

# def active_recording():
#     #feature extraction
#     #measure distance from hyperplane of 2 class SVM
#     #create quality gate to only allow record data points that produces a distance above a threshold


def calibrate(stop_event):
    one_class_svm = get_one_class_svm()
    samples = initial_baseline_recording()
    # Remove the last column (classification label)
    X = samples[:, :-1]
    
    # Fit the one-class SVM
    one_class_svm.fit(X)

    #feature extraction
    #train 1 class SVM
    #initial_active_recording()
    #train a 2 class SVM with
    #baseline recording
    #active recording

if __name__ == "__calibrate__":
    calibrate()
    