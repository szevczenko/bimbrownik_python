from auto_alcohol_distillation import AutoAlcoholDistillation
from scan_devices import ScanDevices

class DeviceManager:
    def __init__(self):
        self.aad_list = list()
        pass

    def close_all(self):
        for aad in self.aad_list:
            aad.stop()

    def scan_devices(self):
        host_list = ScanDevices(scanning_time_s=1)
        self.close_all()
        self.aad_list.clear()
        if len(host_list) == 0:
            return 0
        for host in host_list:
            ip = host[0]
            port = host[1]
            aad = AutoAlcoholDistillation(ip, port)
            self.aad_list.append(aad)
        return len(self.aad_list)
    
    def get_device_count(self):
        return len(self.aad_list)
    
    def __str__(self):
        result = ""
        for aad in self.aad_list:
            result = result + "{" + aad.__str__() + "}; "
        return result
    
if __name__ == "__main__":
    device_manager = DeviceManager()
    device_manager.scan_devices()
    print(device_manager)
    device_manager.close_all()
