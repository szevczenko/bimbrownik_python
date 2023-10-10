# SPDX-FileCopyrightText: 2022 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Unlicense OR CC0-1.0
import http.server
import multiprocessing
import os
import random
import socket
import ssl
import struct
import subprocess
import time
from typing import Callable
from RangeHTTPServer import RangeRequestHandler

server_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_certs/server_cert.pem')
key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_certs/server_key.pem')


def https_request_handler() -> Callable[...,http.server.BaseHTTPRequestHandler]:
    """
    Returns a request handler class that handles broken pipe exception
    """
    class RequestHandler(RangeRequestHandler):
        def finish(self) -> None:
            try:
                if not self.wfile.closed:
                    self.wfile.flush()
                    self.wfile.close()
            except socket.error:
                pass
            self.rfile.close()

        def handle(self) -> None:
            try:
                RangeRequestHandler.handle(self)
            except socket.error:
                pass

    return RequestHandler


def start_https_server(ota_image_dir: str, server_ip: str, server_port: int) -> None:
    os.chdir(ota_image_dir)
    requestHandler = https_request_handler()
    httpd = http.server.HTTPServer((server_ip, server_port), requestHandler)

    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile=key_file,
                                   certfile=server_file, server_side=True)
    httpd.serve_forever()


def start_chunked_server(ota_image_dir: str, server_port: int) -> subprocess.Popen:
    os.chdir(ota_image_dir)
    chunked_server = subprocess.Popen(['openssl', 's_server', '-WWW', '-key', key_file, '-cert', server_file, '-port', str(server_port)])
    return chunked_server


def redirect_handler_factory(url: str) -> Callable[...,http.server.BaseHTTPRequestHandler]:
    """
    Returns a request handler class that redirects to supplied `url`
    """
    class RedirectHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            print('Sending resp, URL: ' + url)
            self.send_response(301)
            self.send_header('Location', url)
            self.end_headers()

        def handle(self) -> None:
            try:
                http.server.BaseHTTPRequestHandler.handle(self)
            except socket.error:
                pass

    return RedirectHandler


def start_redirect_server(ota_image_dir: str, server_ip: str, server_port: int, redirection_port: int) -> None:
    os.chdir(ota_image_dir)
    redirectHandler = redirect_handler_factory('https://' + server_ip + ':' + str(redirection_port) + '/main.bin')

    httpd = http.server.HTTPServer((server_ip, server_port), redirectHandler)

    httpd.socket = ssl.wrap_socket(httpd.socket,
                                   keyfile=key_file,
                                   certfile=server_file, server_side=True)
    httpd.serve_forever()


def test_examples_protocol_advanced_https_ota_example() -> None:
    # Number of iterations to validate OTA
    iterations = 3
    server_port = 8001
    bin_name = 'main.bin'
    # Start server
    start_https_server("./", '192.168.1.155', server_port)
    input(1)
    # thread1.terminate()

# def test_examples_protocol_advanced_https_ota_example_anti_rollback(dut: Dut) -> None:
#     """
#     Working of OTA when anti_rollback is enabled and security version of new image is less than current one.
#     Application should return with error message in this case.
#     steps: |
#       1. join AP/Ethernet
#       2. Generate binary file with lower security version
#       3. Fetch OTA image over HTTPS
#       4. Check working of anti_rollback feature
#     """
#     dut.serial.erase_flash()
#     dut.serial.flash()
#     server_port = 8001
#     # Original binary file generated after compilation
#     bin_name = 'advanced_https_ota.bin'
#     # Modified firmware image to lower security version in its header. This is to enable negative test case
#     anti_rollback_bin_name = 'advanced_https_ota_lower_sec_version.bin'
#     # check and log bin size
#     binary_file = os.path.join(dut.app.binary_path, bin_name)
#     file_size = os.path.getsize(binary_file)
#     with open(binary_file, 'rb+') as f:
#         with open(os.path.join(dut.app.binary_path, anti_rollback_bin_name), 'wb+') as fo:
#             fo.write(f.read(file_size))
#             # Change security_version to 0 for negative test case
#             fo.seek(36)
#             fo.write(b'\x00')
#     binary_file = os.path.join(dut.app.binary_path, anti_rollback_bin_name)
#     # Start server
#     thread1 = multiprocessing.Process(target=start_https_server, args=(dut.app.binary_path, '0.0.0.0', server_port))
#     thread1.daemon = True
#     thread1.start()
#     try:
#         # start test
#         # Positive Case
#         dut.expect('Loaded app from partition at offset', timeout=30)
#         try:
#             ip_address = dut.expect(r'IPv4 address: (\d+\.\d+\.\d+\.\d+)[^\d]', timeout=30)[1].decode()
#             print('Connected to AP/Ethernet with IP: {}'.format(ip_address))
#         except pexpect.exceptions.TIMEOUT:
#             raise ValueError('ENV_TEST_FAILURE: Cannot connect to AP/Ethernet')
#         host_ip = get_host_ip4_by_dest_ip(ip_address)

#         dut.expect('Starting Advanced OTA example', timeout=30)
#         # Use originally generated image with secure_version=1
#         print('writing to device: {}'.format('https://' + host_ip + ':' + str(server_port) + '/' + bin_name))
#         dut.write('https://' + host_ip + ':' + str(server_port) + '/' + bin_name)
#         dut.expect('Loaded app from partition at offset', timeout=60)
#         dut.expect(r'IPv4 address: (\d+\.\d+\.\d+\.\d+)[^\d]', timeout=30)[1].decode()
#         dut.expect(r'App is valid, rollback cancelled successfully', timeout=30)

#         # Negative Case
#         dut.expect('Starting Advanced OTA example', timeout=30)
#         # Use modified image with secure_version=0
#         print('writing to device: {}'.format('https://' + host_ip + ':' + str(server_port) + '/' + anti_rollback_bin_name))
#         dut.write('https://' + host_ip + ':' + str(server_port) + '/' + anti_rollback_bin_name)
#         dut.expect('New firmware security version is less than eFuse programmed, 0 < 1', timeout=30)
#         try:
#             os.remove(binary_file)
#         except OSError:
#             pass
#     finally:
#         thread1.terminate()

if __name__ == "__main__":
    test_examples_protocol_advanced_https_ota_example()
