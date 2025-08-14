import numpy as np

from scipy.signal import welch
import time
# Function to calculate mobility and complexity (Hjorth parameters)
def calculate_hjorth_parameters(signal):
    first_derivative = np.diff(signal)
    second_derivative = np.diff(first_derivative)
    var_signal = np.var(signal)
    var_fd = np.var(first_derivative)
    var_sd = np.var(second_derivative)

    if var_signal < 1e-10 or var_fd < 1e-10:
        return 0.0, 0.0

    mobility = np.sqrt(var_fd / var_signal)
    if mobility < 1e-10:
        return mobility, 0.0

    complexity = np.sqrt(var_sd / var_fd) / mobility
    return mobility, complexity

# Function to calculate bandpowers (alpha and beta)
def calculate_bandpowers(signal, fs=250):
    freqs, psd = welch(signal, fs=fs, nperseg=fs)
    alpha_band = np.logical_and(freqs >= 8, freqs <= 13)
    beta_band = np.logical_and(freqs >= 13, freqs <= 30)
    alpha_power = np.sum(psd[alpha_band])
    beta_power = np.sum(psd[beta_band])
    return alpha_power, beta_power

# function to calculate the log variance
def calculate_log_variance(signal):
    var = np.var(signal)
    if var <= 1e-10:  # very close to 0
        return -10.0  # safe fallback value
    return np.log(var)
