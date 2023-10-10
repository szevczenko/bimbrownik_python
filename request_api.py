import requests
from requests.auth import HTTPBasicAuth

# The API endpoint
url = "http://localhost:8080/default/controller/v1/AAC_000002"

# A GET request to the API
response = requests.get(url, headers={"Content-Type": "application/json", "Authorization": "TargetToken c46ede0de88e64dcb75f36e05fb849ae"})

# Print the response
print(response)
response_json = response.json()
print(response_json)