# SPDX-FileCopyrightText: 2022 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Unlicense OR CC0-1.0
import http.server
import os
import ssl
import sys
from typing import Tuple


def start_http_server(ota_image_dir: str, server_ip: str, server_port: int) -> None:
    os.chdir(ota_image_dir)

    httpd = http.server.HTTPServer((server_ip, server_port), http.server.SimpleHTTPRequestHandler)

    httpd.serve_forever()

if __name__ == '__main__':
    if sys.argv[2:]:    # if two or more arguments provided:
        # Usage: example_test.py <image_dir> <server_port> [cert_di>]
        ip = "192.168.1.144"
        this_dir = os.path.dirname(os.path.realpath(__file__))
        bin_dir = os.path.join(this_dir, sys.argv[1])
        port = int(sys.argv[2])
        cert_dir = bin_dir if not sys.argv[3:] else os.path.join(this_dir, sys.argv[3])  # optional argument
        print(f'Starting HTTPS server at "http://{ip}:{port}"')
        start_http_server(bin_dir, ip, port)
