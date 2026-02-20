import requests
url = "https://assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net/clinical_trials/_count"
auth = ("0204784e62", "38aa998d6c5c2891232c")
try:
    resp = requests.get(url, auth=auth, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.json()}")
except Exception as e:
    print(f"Error: {e}")
