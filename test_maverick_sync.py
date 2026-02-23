
import requests

url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/maverick/chat"
data = {"question": "Are you online, Maverick?"}
try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
