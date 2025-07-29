from process.muse_stream import get_devices_list

class DeviceService:
    def get_devices(self):
        response = get_devices_list()
        return response
