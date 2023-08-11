# echo-server.py

import socket
import time

HOST = "192.168.1.188"  # Standard loopback interface address (localhost)
PORT = 1234  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.send(b'{"setTemperatureSensor":{"sensor":1}}')
    input("Press enter to exit...\n\n")
