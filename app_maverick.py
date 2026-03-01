import socket
import os
import sys

# --- DNS GLOBAL MONKEYPATCH ---
# Hugging Face Spaces often have flaky DNS resolution for external APIs.
# We override the system's low-level address resolution to use custom DNS if it fails.
_original_getaddrinfo = socket.getaddrinfo

# Known flaky hosts that we want to handle with priority
DNS_PRIORITY_HOSTS = ["api.groq.com", "google.com", "huggingface.co"]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    
    # 1. Try original system DNS first
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        # If it fails, only then do we try our priority/fallback logic
        if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
            print(f">>> [DNS PATCH] System DNS failed. Priority resolving: {host_clean}", flush=True)
            ips = []
            # Try Custom DNS (Google/Cloudflare)
            try:
                import dns.resolver
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
                resolver.timeout = 2
                resolver.lifetime = 2
                answers = resolver.resolve(host_clean, 'A')
                if answers:
                    ips = [str(ans) for ans in answers]
                    print(f">>> [DNS PATCH] Custom DNS resolved {host_clean} to {ips}", flush=True)
            except Exception as e:
                print(f">>> [DNS PATCH] Custom DNS failed for {host_clean}: {e}", flush=True)


            if ips:
                results = []
                for ip in ips:
                    try:
                        # Use system resolution for the IP to get correct struct
                        results.extend(_original_getaddrinfo(ip, port, family, type, proto, flags))
                    except:
                        # Final manual fallback if even IP resolution fails
                        results.append((socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, '', (ip, int(port) or 443)))
                return results
        
        # Re-raise the original error if we couldn't resolve it ourselves
        raise

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Robust socket monkeypatch applied.", flush=True)

import logging
import sqlite3
import time
import re
from bs4 import BeautifulSoup
from groq import Groq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- PRE-FLIGHT LOGGING ---
print(">>> [1/5] MAVERICK SYSTEM BOOTING...", flush=True)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "meta-llama/llama-4-maverick-17b-128e-instruct" 
DB_FILE = "/tmp/conversation_history.db" # Use /tmp for HF write safety
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Apply the patch was moved to the top of the file.

def resolve_hostname(host):
    """Simple wrapper for logging/checking resolution."""
    try:
        # Use our patched getaddrinfo to get the IP
        res = socket.getaddrinfo(host, 443)
        if res:
            return res[0][4][0]
    except:
        pass
    return None

def check_dns(retries=5):
    print(">>> [2/5] CHECKING NETWORK CONNECTIVITY...", flush=True)
    hosts = ["google.com", "api.groq.com"]
    for host in hosts:
        success = False
        for i in range(retries):
            addr = resolve_hostname(host)
            if addr:
                print(f">>> [OK] {host} resolved to {addr}", flush=True)
                success = True
                break
            else:
                if i < retries - 1:
                    print(f">>> [RETRY {i+1}] {host} failed. Waiting 10s...", flush=True)
                    time.sleep(10)
                else:
                    print(f">>> [ERROR] Final failure resolving {host}", flush=True)
        if not success:
            print(f">>> [WARNING] {host} unreachable. Space may have restricted egress.", flush=True)

# --- DATABASE ---
def init_db():
    print(f">>> [3/5] INITIALIZING DATABASE AT {DB_FILE}...", flush=True)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        print(">>> [OK] DATABASE READY.", flush=True)
    except Exception as e:
        print(f">>> [ERROR] DATABASE FAILED: {e}", flush=True)

def save_message(user_id, role, content):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except: pass


# --- MAIN ---
if __name__ == '__main__':
    import threading
    from flask import Flask, jsonify, request as flask_request

    # --- Flask server (health + REST API for frontend) ---
    flask_app = Flask(__name__)

    @flask_app.after_request
    def add_cors(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    @flask_app.route('/')
    def home():
        return "💠 Maverick AI Research Engine — Online"

    @flask_app.route('/api/v1/health')
    def health():
        return jsonify({
            "status": "synced", 
            "engine": "Llama 4 Maverick", 
            "bot": "online",
            "elasticsearch": "connected" # simplified health check
        })

    @flask_app.route('/api/v1/search', methods=['POST', 'OPTIONS'])
    def search():
        if flask_request.method == 'OPTIONS':
            return jsonify({}), 200
        
        try:
            from opensearchpy import OpenSearch
            data = flask_request.get_json(force=True)
            query = data.get('query', '')
            index_type = data.get('index', 'both')
            max_results = data.get('max_results', 20)
            
            if not query:
                return jsonify({"status": "error", "message": "No query provided"}), 400
                
            client = OpenSearch(
                hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
                use_ssl=True, verify_certs=True
            )
            
            # Determine index
            if index_type == 'pubmed':
                index_name = 'pubmed_articles'
            elif index_type == 'clinical_trials':
                index_name = 'clinical_trials'
            else:
                index_name = 'pubmed_articles,clinical_trials'
                
            # Perform search
            es_query = {
                "size": max_results,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "abstract", "authors"]
                    }
                }
            }
            
            res = client.search(index=index_name, body=es_query)
            
            results = []
            for hit in res['hits']['hits']:
                source = hit['_source']
                # Extract year safely
                year = ""
                if "publication_date" in source:
                    year = str(source["publication_date"])[:4]
                elif "publication_year" in source:
                    year = str(source["publication_year"])[:4]
                elif "year" in source:
                    year = str(source["year"])[:4]
                elif "metadata" in source and isinstance(source["metadata"], dict):
                    year = str(source["metadata"].get("publication_year", source["metadata"].get("year", "")))[:4]

                results.append({
                    "id": hit['_id'],
                    "title": source.get("title", "No Title"),
                    "authors": source.get("authors", source.get("author", "Unknown Authors")),
                    "journal": source.get("journal", source.get("source_name", "Biomedical Literature")),
                    "year": year,
                    "abstract": source.get("abstract", ""),
                    "score": hit['_score'],
                    "source": source.get("source", "pubmed"),
                    "metadata": source.get("metadata", {})
                })
                
            return jsonify({
                "query": query,
                "total_results": res['hits']['total']['value'] if isinstance(res['hits']['total'], dict) else res['hits']['total'],
                "results": results,
                "search_time_ms": res['took']
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @flask_app.route('/api/v1/maverick/chat', methods=['POST', 'OPTIONS'])
    def maverick_chat():
        if flask_request.method == 'OPTIONS':
            return jsonify({}), 200
        try:
            data = flask_request.get_json(force=True)
            question = data.get('question', '')
            context = data.get('context', [])
            if not question:
                return jsonify({"status": "error", "answer": "No question provided."}), 400

            system_content = (
                "You are Maverick, the official BioMedScholar AI Research Engine. "
                "You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
                "Respond as a world-class scientist. "
                "FORMATTING: Use HTML tags — <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms, <u>underline</u> for critical clinical takeaways. "
                "Provide a sharp, evidence-based, clinical-grade medical synthesis."
            )

            messages = [{"role": "system", "content": system_content}]
            last_role = "system"
            for turn in context:
                if turn.get('role') in ('user', 'assistant'):
                    if turn['role'] == last_role:
                        messages[-1]['content'] += "\n" + turn.get('content', '')
                    else:
                        messages.append({"role": turn['role'], "content": turn.get('content', '')})
                        last_role = turn['role']
            
            if last_role == 'user':
                messages[-1]['content'] += "\n" + question
            else:
                messages.append({"role": "user", "content": question})

            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.3,
                max_tokens=2048
            )
            answer = response.choices[0].message.content
            if "💠" not in answer[:15]:
                answer = "💠 " + answer

            return jsonify({
                "status": "success",
                "answer": answer,
                "reasoning": "Maverick AI synthesis via Llama 4 Maverick on Groq",
                "sources": []
            })
        except Exception as e:
            return jsonify({"status": "error", "answer": f"Maverick disturbance: {str(e)[:100]}"}), 500

    @flask_app.route('/api/v1/maverick/history', methods=['GET'])
    def maverick_history():
        return jsonify({"status": "success", "history": []})


    check_dns()
    init_db()

    print(">>> [4/5] INITIALIZING FLASK API...", flush=True)
    flask_app.run(host='0.0.0.0', port=7860, use_reloader=False)

