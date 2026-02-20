import requests
import json
import sys

def check_health():
    url = "https://sasidhara123-biomed-scholar-api.hf.space/api/v1/health"
    try:
        response = requests.get(url, timeout=15)
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print("Response is not JSON:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_health()
