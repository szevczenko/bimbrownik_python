# echo-server.py

import socket
import time
import threading
import json
from ctypes import *

MAGIC_WORD = 0xDEADBEAF
MAGIC_CTYPE_WORD = c_uint32(MAGIC_WORD)


class TCPClient:
    def __init__(self, ip, port=1234):
        self.ip = ip
        self.port = port
        self.isConnected = False
        self.sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None)
        self.sock.settimeout(1)
        self.iterator = 1
        self.thread = threading.Thread(target=_thread_func, args=(self,))
        self.waitingResponseCallbackArray = list()
        self.thread.start()

    def _prepare_send_data(self, method, data):
        send_data = {"method": method,
                     "i": self.iterator}
        if data is not None:
            send_data["data"] = data
        json_data = create_string_buffer(json.dumps(send_data).encode())
        json_len = c_uint32(len(json_data))
        buff = create_string_buffer(json_len.value + 8)
        memmove(buff, byref(MAGIC_CTYPE_WORD), 4)
        memmove(byref(buff, 4), byref(json_len), 4)
        memmove(byref(buff, 8), addressof(json_data), json_len.value)
        return buff

    def connect(self):
        if self.isConnected is True:
            print("Cannot connect while connection is Active")
            return False
        try:
            self.sock.connect((self.ip, self.port))
        except Exception as error:
            print(error)
            return False
        self.isConnected = True
        return True

    def close(self):
        if self.isConnected is True:
            # W petli pozamykacz wszytkie odpowiedzi
            self.sock.close()
            self.isConnected = False
            return True
        else:
            print("Cannot close connection")
            return False

    def send(self, method, data, response_cb=None, timeout_ms=500):
        # dodac semaphor
        result = False
        if self.isConnected:
            send_data = self._prepare_send_data(method, data)
            len = self.sock.send(send_data)
            if len > 0:
                timeout = time.time_ns() + timeout_ms * 1000000
                wait_response_tuple = (self.iterator, response_cb, timeout)
                if response_cb is not None:
                    self.waitingResponseCallbackArray.append(
                        wait_response_tuple)
                result = True
            self.iterator = self.iterator + 1
        return result

    def wait_to_end(self):
        self.thread.join()


def _check_timeouts(waitedResponseList: list):
    for x in waitedResponseList:
        iterator = x[0]
        callback = x[1]
        timeout = x[2]
        if time.time_ns() > timeout:
            callback(None, None, None, iterator)
            waitedResponseList.remove(x)


def _parse_data(data, waitedResponseList: list):
    i = 0
    while True:
        magic = int.from_bytes(data[i:i + 4], byteorder='little', signed=False)
        if magic == MAGIC_WORD:
            json_len = int.from_bytes(
                data[i + 4:i + 8], byteorder='little', signed=False)
            json_string = data[i + 8: i + 8 + json_len]
            _parse_json(json_string, waitedResponseList)
            i = i + 8 + json_len
        else:
            i = i + 1
        if i >= len(data):
            break


def _parse_json(data, waitedResponseList: list):
    try:
        json_string = data.decode('ascii')
        json_data = json.loads(json_string)
        receive_iterator = json_data["i"]
        for x in waitedResponseList:
            iterator = x[0]
            if receive_iterator == iterator:
                callback = x[1]
                if "msg" in json_data:
                    callback(
                        json_data["error"], json_data["error_str"], json_data["msg"], iterator)
                else:
                    callback(json_data["error"],
                             json_data["error_str"], None, iterator)
                waitedResponseList.remove(x)
    except Exception as error:
        print(error)


def _thread_func(self: TCPClient):
    while True:
        if self.isConnected:
            try:
                data = self.sock.recv(1024)
                _parse_data(data, self.waitingResponseCallbackArray)
            except TimeoutError:
                pass
            except Exception as error:
                print(error)
                self.close()
            _check_timeouts(self.waitingResponseCallbackArray)
        else:
            time.sleep(0.2)


def _response_test(error, error_str, msg, iterator):
    print(f"e: {error}, es: {error_str}, m: {msg}, i: {iterator}")


if __name__ == "__main__":
    host = "192.168.1.188"  # Standard loopback interface address (localhost)
    client = TCPClient(host)
    client.connect()
    client.send("setTemperatureSensor", {"sensor": 1}, _response_test)
    client.send("getDeviceConfig", None, _response_test)
    client.wait_to_end()
