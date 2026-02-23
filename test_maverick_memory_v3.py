
import requests
import json
import sys

url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/maverick/chat"
headers = {"Content-Type": "application/json"}
data = {"question": "Can you remember past information from our previous conversations?"}

try:
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    # Print the answer specifically with clear delimiters
    print("START_ANSWER")
    print(result.get("answer", "No answer found"))
    print("END_ANSWER")
except Exception as e:
    print(f"ERROR: {e}")
