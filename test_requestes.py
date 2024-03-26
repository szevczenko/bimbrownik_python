import requests
from scan_devices import ScanDevices


result = ScanDevices(name="Production", scanning_time_s=1)

url = f"http://{result[0][0]}:8000/api/sn"

# A GET request to the API
session = requests.Session()

response = session.get(url)
print(response.text)

url = f"http://{result[0][0]}:8000/api/ota"
response = session.post(url, "http://192.168.1.144/main.bin")
print(response.text)
