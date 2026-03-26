import requests
import json

url = "https://assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"
auth = ("0204784e62", "38aa998d6c5c2891232c")

def debug_connection():
    try:
        print(f"Connecting to: {url}")
        # Try a simple GET to root
        response = requests.get(url, auth=auth, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response (text): {response.text}")
            
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    debug_connection()
