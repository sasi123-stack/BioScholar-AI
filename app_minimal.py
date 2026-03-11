"""
BioMed Scholar API - FastAPI version with Maverick AI integration.
Includes search, chat, and historical research capabilities.
"""

import socket
import os
import sys
import sqlite3
import time
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# --- DNS PATCH FOR HUGGING FACE SPACES ---
_original_getaddrinfo = socket.getaddrinfo
DNS_PRIORITY_HOSTS = ["api.groq.com", "google.com", "huggingface.co"]

def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    host_str = host.decode('utf-8') if isinstance(host, bytes) else str(host)
    host_clean = host_str.lower().strip('.')
    
    try:
        return _original_getaddrinfo(host, port, family, type, proto, flags)
    except Exception:
        if any(h in host_clean for h in DNS_PRIORITY_HOSTS):
            print(f">>> [DNS PATCH] System DNS failed. Trying custom DNS for: {host_clean}", flush=True)
            try:
                import dns.resolver
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
                resolver.timeout = 2
                resolver.lifetime = 2
                answers = resolver.resolve(host_clean, 'A')
                if answers:
                    ips = [str(ans) for ans in answers]
                    results = []
                    for ip in ips:
                        try:
                            results.extend(_original_getaddrinfo(ip, port, family, type, proto, flags))
                        except:
                            results.append((socket.AF_INET, type or socket.SOCK_STREAM, proto or 6, '', (ip, int(port) or 443)))
                    return results
            except Exception as e:
                print(f">>> [DNS PATCH] Custom DNS failed: {e}", flush=True)
        raise

socket.getaddrinfo = custom_getaddrinfo
print(">>> [DNS PATCH] Applied robust socket monkeypatch", flush=True)

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"
DB_FILE = "/tmp/conversation_history.db"
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

# --- PYDANTIC MODELS ---
class SearchRequest(BaseModel):
    query: str
    index: str = "both"
    max_results: int = 20

class ChatRequest(BaseModel):
    question: str
    context: List[Dict[str, str]] = []

# --- DATABASE ---
def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
        print(">>> [DB] Initialized conversation history", flush=True)
        return True
    except Exception as e:
        print(f">>> [DB ERROR] {e}", flush=True)
        return False

def save_message(user_id: int, role: str, content: str):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        conn.commit()
        conn.close()
    except:
        pass

# --- ELASTICSEARCH/OPENSEARCH FUNCTIONS ---
def get_elasticsearch_stats() -> Dict[str, Any]:
    try:
        from opensearchpy import OpenSearch
        client = OpenSearch(
            hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
            use_ssl=True, verify_certs=True
        )
        
        stats = {}
        for index_name in ["pubmed_articles", "clinical_trials"]:
            try:
                res = client.count(index=index_name)
                stats[index_name] = {
                    "document_count": res['count'],
                    "index_exists": True
                }
            except:
                stats[index_name] = {
                    "document_count": 0,
                    "index_exists": False
                }
        return stats
    except Exception as e:
        logger.warning(f"ES connection failed: {e}")
        return {}

# --- FASTAPI APP ---
app = FastAPI(
    title="BioMed Scholar API",
    description="AI-powered biomedical research engine with Maverick AI",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (serves favicon.ico, etc.)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    print(">>> [STARTUP] Initializing BioMed Scholar API...", flush=True)
    init_db()
    print(">>> [STARTUP] API ready", flush=True)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "💠 BioMed Scholar AI Research Engine",
        "version": "2.0.0",
        "docs": "/docs",
        "features": {
            "search": "/api/v1/search",
            "chat": "/api/v1/maverick/chat",
            "health": "/api/v1/health",
            "statistics": "/api/v1/statistics"
        }
    }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon from static folder."""
    favicon_path = os.path.join(os.path.dirname(__file__), "static", "favicon.svg")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/svg+xml")
    return {"message": "favicon not found"}

@app.get("/api/v1/health")
async def health():
    """Health check endpoint."""
    es_stats = get_elasticsearch_stats()
    es_healthy = bool(es_stats and any(s.get("index_exists") for s in es_stats.values()))
    groq_healthy = bool(GROQ_API_KEY)
    
    return {
        "status": "synced",
        "version": "2.0.0",
        "engine": "Maverick AI",
        "services": {
            "elasticsearch": es_healthy,
            "groq": groq_healthy,
            "database": True
        },
        "features": {
            "search_enabled": es_healthy,
            "chat_enabled": groq_healthy,
            "history_enabled": True
        }
    }

@app.get("/api/v1/statistics")
async def statistics():
    """Get statistics from Elasticsearch/OpenSearch."""
    try:
        stats = get_elasticsearch_stats()
        return {
            "pubmed_articles": stats.get("pubmed_articles", {}).get("document_count", 0),
            "clinical_trials": stats.get("clinical_trials", {}).get("document_count", 0),
            "total_documents": sum(s.get("document_count", 0) for s in stats.values())
        }
    except Exception as e:
        return {"error": str(e), "total_documents": 0}

@app.post("/api/v1/search")
async def search(request: SearchRequest):
    """Search biomedical literature and clinical trials."""
    try:
        from opensearchpy import OpenSearch
        
        if not request.query:
            raise HTTPException(status_code=400, detail="No query provided")
        
        client = OpenSearch(
            hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
            use_ssl=True, verify_certs=True
        )
        
        # Determine index
        if request.index == 'pubmed':
            index_name = 'pubmed_articles'
        elif request.index == 'clinical_trials':
            index_name = 'clinical_trials'
        else:
            index_name = 'pubmed_articles,clinical_trials'
        
        # Perform search
        es_query = {
            "size": request.max_results,
            "query": {
                "multi_match": {
                    "query": request.query,
                    "fields": ["title^3", "abstract", "authors"]
                }
            }
        }
        
        res = client.search(index=index_name, body=es_query)
        
        results = []
        for hit in res['hits']['hits']:
            source = hit['_source']
            year = ""
            if "publication_date" in source:
                year = str(source["publication_date"])[:4]
            elif "publication_year" in source:
                year = str(source["publication_year"])[:4]
            elif "year" in source:
                year = str(source["year"])[:4]
            
            results.append({
                "id": hit['_id'],
                "title": source.get("title", "No Title"),
                "authors": source.get("authors", source.get("author", "Unknown")),
                "journal": source.get("journal", source.get("source_name", "Biomedical Literature")),
                "year": year,
                "abstract": source.get("abstract", ""),
                "score": hit['_score'],
                "source": source.get("source", "pubmed")
            })
        
        return {
            "query": request.query,
            "total_results": res['hits']['total']['value'] if isinstance(res['hits']['total'], dict) else res['hits']['total'],
            "results": results,
            "search_time_ms": res['took']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/maverick/chat")
async def maverick_chat(request: ChatRequest):
    """Chat with Maverick AI using GPT OSS 120B."""
    try:
        if not GROQ_API_KEY:
            raise HTTPException(status_code=503, detail="Groq API not configured")
        
        if not request.question:
            raise HTTPException(status_code=400, detail="No question provided")
        
        from groq import AsyncGroq
        
        system_content = (
            "You are Maverick, the official BioMedScholar AI Research Engine. "
            "You are a high-performance, elite analytical assistant specialized in human medicine, oncology, and pharmacology. "
            "Respond as a world-class scientist. "
            "FORMATTING: Use HTML tags — <b>bold</b> for primary medical terms, <i>italic</i> for Latin terms, <u>underline</u> for critical clinical takeaways. "
            "Provide a sharp, evidence-based, clinical-grade medical synthesis."
        )
        
        messages = [{"role": "system", "content": system_content}]
        last_role = "system"
        
        for turn in request.context:
            if turn.get('role') in ('user', 'assistant'):
                if turn['role'] == last_role:
                    messages[-1]['content'] += "\n" + turn.get('content', '')
                else:
                    messages.append({"role": turn['role'], "content": turn.get('content', '')})
                    last_role = turn['role']
        
        if last_role == 'user':
            messages[-1]['content'] += "\n" + request.question
        else:
            messages.append({"role": "user", "content": request.question})
        
        client = AsyncGroq(api_key=GROQ_API_KEY)
        models_to_try = [MODEL_NAME, "llama-3.3-70b-versatile", "llama3-70b-8192"]
        answer = None
        
        for model in models_to_try:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2048
                )
                temp_answer = response.choices[0].message.content
                if temp_answer and ("<!DOCTYPE" in temp_answer[:20] or "<html>" in temp_answer.lower()[:20]):
                    logger.warning(f"Model {model} returned HTML error. Trying next...")
                    continue
                answer = temp_answer
                break
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                continue
        
        if not answer:
            answer = "❌ <b>Maverick System Error</b>: Upstream AI interface is currently unstable. Please try again in 1 minute."
        elif "💠" not in answer[:15]:
            answer = "💠 " + answer
        
        return {
            "status": "success",
            "answer": answer,
            "reasoning": "Maverick AI synthesis via GPT OSS 120B on Groq",
            "sources": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/maverick/history")
async def maverick_history(user_id: int = 1):
    """Get conversation history for a user."""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT role, content, timestamp FROM history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50", (user_id,))
        rows = c.fetchall()
        conn.close()
        
        return {
            "status": "success",
            "user_id": user_id,
            "history": [
                {"role": row[0], "content": row[1], "timestamp": row[2]}
                for row in reversed(rows)
            ]
        }
    except:
        return {"status": "success", "user_id": user_id, "history": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app_minimal:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
