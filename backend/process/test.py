import threading
from calibration import calibrate
def main():
    record_data_event = threading.Event()
    calibrate(record_data_event)

if __name__ == '__main__':
    main()