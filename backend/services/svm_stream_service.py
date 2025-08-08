import time

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