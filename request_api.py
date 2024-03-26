import requests
from requests.auth import HTTPBasicAuth

# cert = "C:\projekty\hawkbit\hawkbit-runtime\docker\cert.pem" #"C:\projekty\hawkbit\hawkbit-runtime\docker\cert.pem" #, "C:\projekty\hawkbit\hawkbit-runtime\docker\myKey.pem")

# The API endpoint
url = "https://localhost:8443/default/controller/v1/AAD_000001"

# A GET request to the API
session = requests.Session()
response = session.get(url, verify=False, headers={"Content-Type": "application/json", "Authorization": "TargetToken d8542ad550fef419a6bf1189babf58ab"})

# Print the response
print(response)
response_json = response.json()
print(response_json)

url = "http://localhost:8080/default/controller/v1/AAD_000001"


# response = requests.post(url, data='{"id":"6","status":{"result":{"finished":"success"},"execution":"closed","details":["The update was successfully installed."]}}', headers={"Content-Type": "application/json", "Authorization": "TargetToken d8542ad550fef419a6bf1189babf58ab"})
print(response)
