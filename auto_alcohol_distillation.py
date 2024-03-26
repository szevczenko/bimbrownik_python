import socket
import time

# import mdns
import tcp_client
import threading
from queue import Queue


class AutoAlcoholDistillation:
    def __init__(self, ip, port=1234) -> None:
        self.ip = ip
        self.client = tcp_client.TCPClient(ip, port)
        self.isConnected = False
        self.waitResponseList = list()
        self.project = "UNKNOWN"
        self.sn = "-1"
        self.connect()
        self.getAllParameters()

    def getAllParameters(self):
        if self.getDeviceConfig() == False:
            return False
        self.getOtaConfig()
        self.getMQTTConfig()
        return True

    def connect(self):
        if self.isConnected == True:
            return True
        self.isConnected = self.client.connect()
        return self.isConnected

    def stop(self):
        self.client.stop()

    def _sendRequest(self, method: str, data: dict = None, timeout=500):
        queue = Queue()
        iterator = self.client.send(method, data, readDataCallback, self, timeout)
        if None == iterator:
            return None
        self.waitResponseList.append((queue, iterator))
        data = queue.get()
        return data

    def getDeviceConfig(self):
        data = self._sendRequest("getDeviceConfig")
        if data is not None:
            error = data[0]
            read_data = data[2]
            if error == 0:
                self.sw = read_data["sw"]
                self.project = read_data["project"]
                self.sn = read_data["sn"]
                return True
        return False

    def getOtaConfig(self):
        data = self._sendRequest("getOTA")
        if data is not None:
            error = data[0]
            read_data = data[2]
            if error == 0:
                self.address = read_data["address"]
                self.tenant = read_data["tenant"]
                self.tls = read_data["tls"]
                self.poll_time = read_data["poll_time"]
                self.token = read_data["token"]
                return True
        return False

    def getMQTTConfig(self):
        data = self._sendRequest("getMQTT")
        if data is not None:
            error = data[0]
            read_data = data[2]
            print(data)
            if error == 0:
                self.mqtt_address = read_data["address"]
                self.mqtt_prefix_topic = read_data["prefix"]
                self.mqtt_data_topic = read_data["data"]
                self.mqtt_username = read_data["user"]
                self.mqtt_password = read_data["pass"]
                self.ssl = read_data["ssl"]
                return True
        return False

    def setOtaConfig(
        self, address, tenant="default", tls=True, poll_time=100, token=None
    ):
        send_data = {
            "address": address,
            "tenant": tenant,
            "tls": tls,
            "poll_time": poll_time,
        }
        if token is not None:
            send_data["token"] = token

        response = self._sendRequest("setOTA", send_data)
        if response[0] == 0:
            response = self._sendRequest("saveOTA", send_data)
            if response[0] == 0:
                self.address = address
                self.tenant = tenant
                self.tls = tls
                self.poll_time = poll_time
                if token is not None:
                    self.token = token
                return True
        print(response)
        return False

    def setMQTTConfig(
        self,
        address,
        prefix="/prefix",
        data="/data",
        username="new_user_ha_ha",
        password="",
        ssl=False,
    ):
        send_data = {
            "address": address,
            "ssl": ssl,
            "user": username,
            "pass": password,
            "prefix": prefix,
            "data": data,
        }

        response = self._sendRequest("setMQTT", send_data)
        if response[0] == 0:
            response = self._sendRequest("saveMQTT", send_data)
            if response[0] == 0:
                self.mqtt_address = address
                self.mqtt_prefix_topic = prefix
                self.mqtt_data_topic = data
                self.mqtt_username = username
                self.mqtt_password = password
                self.ssl = ssl
                return True
        print(response)
        return False

    def setMQTTCert(self, cert_path):
        response = (-1, None, None)
        with open(cert_path, "r") as file:
            offset = 0
            while True:
                file_read = file.read(256)
                if len(file_read) == 0:
                    break
                send_data = {
                    "offset": offset,
                    "len": len(file_read),
                    "cert": file_read,
                }
                response = self._sendRequest("setMQTTCert", send_data)
                offset += len(file_read)
        if response[0] == 0:
            response = self._sendRequest("saveMQTT", send_data)
            if response[0] == 0:
                return True
        return False
    
    def getMQTTCert(self, read_cert="read_cert.pem"):
        response = (-1, None, None)
        with open(read_cert, "w") as file:
            offset = 0
            while True:
                send_data = {
                    "offset": offset,
                }
                response = self._sendRequest("getMQTTCert", send_data)
                read_data = response[2]
                print(response)
                if response[0] == 0 and read_data["cert"] != "":
                    file.write(read_data["cert"])
                else:
                    break             
                offset += len(read_data["cert"])
        if response[0] == 0:
            return True
        return False

    def __str__(self) -> str:
        result = f"dev: {self.project}_{self.sn}, host: {self.ip}"
        return result


def readDataCallback(self: AutoAlcoholDistillation, error, error_str, msg, iterator):
    for x in self.waitResponseList:
        if x[1] == iterator:
            queue = x[0]
            queue.put((error, error_str, msg))
            self.waitResponseList.remove(x)


if __name__ == "__main__":
    host = "192.168.1.246"  # Standard loopback interface address (localhost)
    bimbrownik = AutoAlcoholDistillation(host)
    # bimbrownik.setMQTTConfig("mqtt://homeassistant.local:1883", "/con1", "data3", "homeassistant", "12345678", False)
    bimbrownik.getMQTTConfig()
    # bimbrownik.setMQTTCert("servercert.pem")
    # bimbrownik.getMQTTCert()
    print(bimbrownik)
    bimbrownik.stop()
