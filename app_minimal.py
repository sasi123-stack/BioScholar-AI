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
import httpx
import base64
from typing import List, Dict, Any, Optional

# Ensure 'src' is in path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# --- DNS PATCH FOR HUGGING FACE SPACES ---
_original_getaddrinfo = socket.getaddrinfo
DNS_PRIORITY_HOSTS = ["api.groq.com", "google.com", "huggingface.co", "openrouter.ai", "ncbi.nlm.nih.gov"]

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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", os.getenv("OPENCLAW_API_KEY"))
MODEL_NAME = "gpt-oss:120b"
VISION_MODEL = "meta-llama/llama-3.2–11b-vision-instruct:free"
DB_FILE = "/tmp/conversation_history.db" if os.path.exists("/tmp") else "local_memory.db"
ES_HOST = os.getenv("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net")
ES_USER = os.getenv("ELASTICSEARCH_USER", "0204784e62")
ES_PASS = os.getenv("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c")

OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# --- PYDANTIC MODELS ---
class SearchRequest(BaseModel):
    query: str
    index: str = "both"
    max_results: int = 50
    date_from: Optional[int] = None
    date_to: Optional[int] = None
    article_types: Optional[List[str]] = None
    subject: Optional[str] = None
    availability: Optional[str] = None
    sort_by: Optional[str] = "relevance"

class ChatRequest(BaseModel):
    question: str
    context: List[Dict[str, str]] = []

class Attachment(BaseModel):
    name: str
    type: str
    data: str

class ChatWithImageRequest(BaseModel):
    question: str
    attachments: List[Attachment] = []
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

# --- FALLBACK SEARCH (ENTREZ) ---
def fallback_search_entrez(query: str, max_results: int = 20) -> List[Dict]:
    """Fallback search using NCBI Entrez API."""
    try:
        from src.data_pipeline.pubmed_fetcher import PubMedFetcher
        fetcher = PubMedFetcher(email="biomed-scholar-user@example.com")
        
        # Simple search usingEntrez
        detailed_articles = fetcher.search_and_fetch(query, max_results=max_results)
        
        results = []
        for doc in detailed_articles:
            results.append({
                "id": doc.get("pmid", "unknown"),
                "title": doc.get("title", "No Title"),
                "authors": doc.get("authors", []),
                "journal": doc.get("journal", "PubMed"),
                "year": doc.get("publication_year", ""),
                "abstract": doc.get("abstract", ""),
                "score": 1.0, # Flat score for fallback
                "source": "pubmed (live)"
            })
        return results
    except Exception as e:
        logger.error(f"Fallback search failed: {e}")
        return []

# --- FASTAPI APP ---
app = FastAPI(
    title="BioMed Scholar API",
    description="AI-powered biomedical research engine with Maverick AI",
    version="2.1.0"
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
        "version": "2.1.3",
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
        "version": "2.1.0",
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

@app.get("/api/v1/diagnostic")
async def diagnostic():
    """Diagnostic endpoint for checking system health and fallbacks."""
    entrez_test = False
    error = None
    try:
        from app_minimal import fallback_search_entrez
        results = fallback_search_entrez("cancer", max_results=1)
        entrez_test = len(results) > 0
    except Exception as e:
        error = str(e)
        
    return {
        "bonsai": False,
        "entrez": entrez_test,
        "entrez_error": error,
        "version": "2.1.3",
        "env": "production"
    }

@app.post("/api/v1/search")
async def search(request: SearchRequest):
    """Search biomedical literature and clinical trials with live fallback."""
    try:
        from opensearchpy import OpenSearch
        
        if not request.query:
            return {
                "query": "",
                "total_results": 0,
                "results": [],
                "search_time_ms": 0,
                "warning": "No query provided"
            }
        
        # Attempt Primary: OpenSearch (Bonsai)
        try:
            client = OpenSearch(
                hosts=[f"https://{ES_USER}:{ES_PASS}@{ES_HOST}:443"],
                use_ssl=True, verify_certs=True,
                timeout=3 # Aggressive timeout
            )
            
            # Index logic
            if request.index == 'pubmed':
                index_name = 'pubmed_articles'
            elif request.index == 'clinical_trials':
                index_name = 'clinical_trials'
            else:
                index_name = 'pubmed_articles,clinical_trials'
            
            # Simple query (faster)
            es_query = {
                "size": request.max_results,
                "query": {
                    "match": {
                        "title": request.query
                    }
                }
            }
            
            res = client.search(index=index_name, body=es_query)
            
            results = []
            for hit in res['hits']['hits']:
                source = hit['_source']
                results.append({
                    "id": hit['_id'],
                    "title": source.get("title", "No Title"),
                    "authors": source.get("authors", "Unknown"),
                    "journal": source.get("journal", "Biomedical Literature"),
                    "year": str(source.get("publication_year", source.get("year", "")))[:4],
                    "abstract": source.get("abstract", ""),
                    "score": hit['_score'],
                    "source": source.get("source", "pubmed")
                })
            
            return {
                "query": request.query,
                "total_results": len(results),
                "results": results,
                "search_time_ms": res['took']
            }
            
        except Exception as es_err:
            logger.warning(f"Bonsai index offline ({es_err}). Switching to Entrez...")
            
            # FALLBACK START
            fallback_results = fallback_search_entrez(request.query, max_results=request.max_results)
            
            # ALWAYS return 200 even if fallback is empty
            return {
                "query": request.query,
                "total_results": len(fallback_results),
                "results": fallback_results,
                "search_time_ms": 0,
                "warning": "Primary search index (Bonsai) is unavailable. Displaying live PubMed results."
            }

    except Exception as e:
        logger.error(f"Search endpoint critical failure: {e}")
        return {
            "query": request.query,
            "total_results": 0,
            "results": [],
            "search_time_ms": 0,
            "warning": f"Search unavailable: {str(e)}"
        }

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

async def get_vision_completion(prompt: str, image_base64: str):
    """Get completion from a vision model via OpenRouter."""
    if not OPENROUTER_API_KEY:
        raise Exception("OPENROUTER_API_KEY is not configured.")

    # The data URL is already base64 encoded, so we just need to extract the raw base64 data
    try:
        header, encoded = image_base64.split(",", 1)
    except ValueError:
        raise Exception("Invalid base64 image data")

    async with httpx.AsyncClient(timeout=45.0) as client:
        try:
            logger.info(f"Querying vision model '{VISION_MODEL}'")
            response = await client.post(
                f"{OPENROUTER_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                                },
                            ],
                        }
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']

        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter vision API error: {e.response.status_code} {e.response.text}")
            raise Exception(f"Vision API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Vision completion error: {e}")
            raise

@app.post("/api/v1/maverick/chat_with_image")
async def maverick_chat_with_image(request: ChatWithImageRequest):
    """Chat with Maverick AI using a vision model."""
    try:
        if not OPENROUTER_API_KEY:
            raise HTTPException(status_code=503, detail="OpenRouter API not configured")

        if not request.question:
            raise HTTPException(status_code=400, detail="No question provided")

        if not request.attachments:
            raise HTTPException(status_code=400, detail="No image provided")

        # For now, we only support one image
        image_attachment = request.attachments[0]

        answer = await get_vision_completion(request.question, image_attachment.data)

        if "💠" not in answer[:15]:
            answer = "💠 " + answer

        return {
            "status": "success",
            "answer": answer,
            "reasoning": "Maverick AI vision analysis via OpenRouter",
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
