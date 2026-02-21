
import requests
import json

url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/maverick/chat"
data = {"question": "Can you remember past information from our previous conversations?"}

print(f"Testing Maverick Memory at: {url}")
try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print("\nMaverick's Response:")
    print("-" * 30)
    print(result.get("answer"))
    print("-" * 30)
except Exception as e:
    print(f"Error: {e}")
