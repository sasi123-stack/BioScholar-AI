import requests
import sys

def check_url(url):
    try:
        print(f"Checking: {url}")
        response = requests.get(url, timeout=10, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Content: {response.text[:200]}")
        if response.status_code in [301, 302, 307, 308]:
             print(f"Redirect Location: {response.headers.get('Location')}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
    print("-" * 20)

if __name__ == "__main__":
    base_url = "https://sasidhara123-biomed-scholar-api.hf.space"
    check_url(f"{base_url}/")
    check_url(f"{base_url}/health")
    check_url(f"{base_url}/api/v1/health")
    check_url(f"{base_url}/docs")
