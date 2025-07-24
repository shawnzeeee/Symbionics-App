import numpy as np

def check_signal(eeg_buffer):
    # eeg_buffer shape: (num_samples, num_channels)
    eeg_buffer = eeg_buffer.reshape(500,4)
    for i in range(eeg_buffer.shape[1]):
        channel_data = eeg_buffer[:, i]
        variance = channel_data.std()
        print(f"Channel {i} variance: {variance}")