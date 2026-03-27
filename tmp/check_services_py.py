
import socket
import requests

def check_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError, socket.error):
        return False

def check_services():
    services = [
        {"name": "Elasticsearch (Local 9201)", "host": "localhost", "port": 9201},
        {"name": "Elasticsearch (Local 9200)", "host": "localhost", "port": 9200},
        {"name": "Redis (Local 6380)", "host": "localhost", "port": 6380},
        {"name": "Redis (Local 6379)", "host": "localhost", "port": 6379},
        {"name": "PostgreSQL (Local 5433)", "host": "localhost", "port": 5433},
        {"name": "PostgreSQL (Local 5432)", "host": "localhost", "port": 5432},
        {"name": "Bonsai ES (Remote)", "url": "https://assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net/_cluster/health", "auth": ("0204784e62", "38aa998d6c5c2891232c")}
    ]

    print("Checking BioMed Scholar Services Status:")
    print("-" * 50)

    for svc in services:
        if "url" in svc:
            try:
                resp = requests.get(svc["url"], auth=svc["auth"], timeout=5)
                if resp.status_code == 200:
                    status = "ACTIVE"
                    info = f"Cluster Status: {resp.json().get('status', 'unknown')}"
                else:
                    status = f"Error {resp.status_code}"
                    info = ""
            except Exception as e:
                status = "INACTIVE"
                info = str(e)
            print(f"{svc['name']:<35}: {status} {info}")
        else:
            is_active = check_port(svc["host"], svc["port"])
            status = "ACTIVE" if is_active else "INACTIVE"
            print(f"{svc['name']:<35}: {status}")

if __name__ == "__main__":
    check_services()
