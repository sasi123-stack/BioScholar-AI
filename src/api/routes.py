"""
API route handlers for biomedical search engine.
"""

import time
import httpx
from src.api.models import (
    SearchRequest,
    SearchResponse,
    QuestionRequest,
    QuestionResponse,
    DocumentResponse,
    HealthResponse,
    BatchQuestionRequest,
    BatchQuestionResponse,
    DocumentIngestRequest,
    BatchDocumentIngestRequest,
    IngestResponse,
    DocumentResult,
    AnswerResult,
    PassageResult
)

from src.api.dependencies import (
    get_settings,
    get_search_engine,
    get_reranker,
    get_qa_engine,
    get_document_indexer
)
from src.search_engine.hybrid_search import HybridSearchEngine
from src.search_engine.reranker import CrossEncoderReranker
from src.qa_module.qa_engine import QuestionAnsweringEngine
from src.indexing.document_indexer import DocumentIndexer
from src.utils.config import Settings
from src.utils.logger import logger
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

import sqlite3
import os

router = APIRouter(prefix="/api/v1", tags=["api"])

# Shared Maverick DB - Must match app_maverick.py
MAVERICK_DB = "/tmp/conversation_history.db" if os.path.exists("/tmp") else "local_memory.db"


@router.get("/health", response_model=HealthResponse)
async def health_check(
    search_engine: HybridSearchEngine = Depends(get_search_engine),
    settings: Settings = Depends(get_settings)
):
    """
    Health check endpoint.
    
    Returns service status and connectivity information.
    """
    try:
        # Check Elasticsearch connection
        es_connected = search_engine.es_client.is_connected()
        
        # Check which features are enabled
        qa_engine = get_qa_engine()
        reranker = get_reranker()
        
        return HealthResponse(
            status="healthy" if es_connected else "degraded",
            elasticsearch=es_connected,
            models_loaded=qa_engine is not None,
            version="1.0.0",
            features={
                "qa_enabled": qa_engine is not None,
                "reranking_enabled": reranker is not None
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            elasticsearch=False,
            models_loaded=False,
            version="1.0.0"
        )

@router.get("/bot-logs")
async def get_bot_logs():
    """
    Diagnostic endpoint to view Maverick Bot background logs.
    """
    import os
    log_path = "/tmp/maverick_bot.log"
    if not os.path.exists(log_path):
        return {"status": "not_found", "message": f"Log file at {log_path} does not exist yet."}
    
    try:
        with open(log_path, "r") as f:
            # Get last 100 lines
            lines = f.readlines()
            last_lines = lines[-100:] if len(lines) > 100 else lines
            return {
                "status": "success",
                "log_file": log_path,
                "line_count": len(lines),
                "logs": last_lines
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    search_engine: HybridSearchEngine = Depends(get_search_engine),
    reranker: CrossEncoderReranker = Depends(get_reranker),
    settings: Settings = Depends(get_settings)
):
    """
    Search for documents using hybrid search or Google Serper.
    """
    try:
        start_time = time.time()
        document_results = []
        
        if request.index == "google":
            # Perform Google Search via Serper
            if not settings.serper_api_key or settings.serper_api_key == "YOUR_SERPER_API_KEY_HERE":
                logger.warning("Serper API key not configured on backend")
                # Don't throw 500, return empty results with a message
                return SearchResponse(
                    query=request.query,
                    total_results=0,
                    results=[],
                    search_time_ms=round((time.time() - start_time) * 1000, 2)
                )

            logger.info(f"Performing Google Search via Serper for: '{request.query}'")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": settings.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": request.query,
                        "num": request.max_results
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Serper API failed: {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=f"Serper API failed: {response.text}")
                
                serper_data = response.json()
                for i, item in enumerate(serper_data.get("organic", [])):
                    document_results.append(DocumentResult(
                        id=f"google-{i}",
                        title=item.get("title") or "No Title",
                        abstract=item.get("snippet") or "No snippet available.",
                        score=1.0 - (i * 0.01),
                        source="google",
                        metadata={
                            "authors": ["Web Content"],
                            "publication_date": item.get("date") or "N/A",
                            "journal": httpx.URL(item.get("link")).host if item.get("link") else "N/A",
                            "url": item.get("link")
                        }
                    ))
        else:
            # Existing Elasticsearch logic
            # Determine index to search
            if request.index == "pubmed":
                index_name = "pubmed_articles"
            elif request.index == "clinical_trials":
                index_name = "clinical_trials"
            else:  # both
                index_name = "all"
            
            # Perform hybrid search
            logger.info(f"Searching '{request.query}' in {index_name}")
            results = search_engine.hybrid_search(
                index_name=index_name,
                query=request.query,
                size=request.max_results,
                alpha=request.alpha,
                sort_by=request.sort_by,
                date_from=request.date_from,
                date_to=request.date_to,
                article_types=request.article_types,
                subject=request.subject,
                availability=request.availability
            )
            
            # Apply reranking if requested and available
            if request.use_reranking and results:
                if reranker is not None:
                    logger.info("Applying cross-encoder reranking")
                    results = reranker.rerank(request.query, results)
                else:
                    logger.warning("Reranking requested but disabled (LOW_MEMORY_MODE)")
            
            # Ensure results are sorted by score (descending)
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Convert to response format
            for result in results:
                source = result.get("source", {})
                doc_id = result.get("id", "")
                
                if "source" in source and source["source"]:
                    source_type = source["source"]
                elif "pmid" in source and source["pmid"]:
                    source_type = "pubmed"
                elif "nct_id" in source and source["nct_id"]:
                    source_type = "clinical_trials"
                else:
                    source_type = "pubmed" if index_name == "pubmed_articles" else "clinical_trials"
                
                document_results.append(DocumentResult(
                    id=doc_id,
                    title=source.get("title") or "No Title",
                    abstract=source.get("abstract") or "No abstract available.",
                    score=result.get("score") or 0.0,
                    source=source_type,
                    metadata={
                        "authors": source.get("authors") or [],
                        "publication_date": source.get("publication_date") or source.get("publication_year") or source.get("year") or source.get("start_date") or "N/A",
                        "journal": source.get("journal") or "N/A",
                        "pmid": source.get("pmid"),
                        "nct_id": source.get("nct_id")
                    }
                ))
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            total_results=len(document_results),
            results=document_results,
            search_time_ms=round(search_time_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/question", response_model=QuestionResponse)
async def answer_question(
    request: QuestionRequest,
    qa_engine: QuestionAnsweringEngine = Depends(get_qa_engine)
):
    """
    Answer a question using biomedical literature.
    
    Retrieves relevant passages and extracts answers using BioBERT QA model.
    Returns answers with confidence scores and source information.
    """
    # Check if QA engine is available
    if qa_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Q&A feature unavailable (LOW_MEMORY_MODE enabled). Upgrade to enable this feature."
        )
    
    try:
        start_time = time.time()
        
        # Determine index to search
        if request.index == "pubmed":
            index_name = "pubmed_articles"
        elif request.index == "clinical_trials":
            index_name = "clinical_trials"
        else:  # both
            index_name = "all"
        
        # Answer the question
        logger.info(f"Answering question: '{request.question}'")
        result = qa_engine.answer_question(
            question=request.question,
            index_name=index_name,
            num_answers=request.max_answers,
            num_passages=request.max_passages
        )
        
        # Convert to response format
        answers = []
        for ans in result.get("answers", []):
            answers.append(AnswerResult(
                answer=ans.get("answer") or "",
                confidence=ans.get("confidence") or 0.0,
                confidence_level=ans.get("confidence_level") or "low",
                source_title=ans.get("title") or "No Title",
                source_id=ans.get("doc_id") or "unknown",
                source_type=ans.get("source_type") or "unknown",
                section=ans.get("section") or "abstract",
                context=ans.get("context"),
                journal=ans.get("journal"),
                publication_date=ans.get("publication_date")
            ))
        
        passages = []
        for passage in result.get("passages", []):
            passages.append(PassageResult(
                text=(passage.get("text") or "")[:500],  # Truncate long passages
                score=passage.get("score") or 0.0,
                source_title=passage.get("title") or "No Title",
                source_id=passage.get("doc_id") or "unknown",
                section=passage.get("section") or "abstract"
            ))
        
        qa_time_ms = (time.time() - start_time) * 1000
        
        return QuestionResponse(
            question=request.question,
            status=result["status"],
            answers=answers,
            passages=passages,
            qa_time_ms=round(qa_time_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Question answering failed: {e}")
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")


@router.post("/batch-question", response_model=BatchQuestionResponse)
async def batch_answer_questions(
    request: BatchQuestionRequest,
    qa_engine: QuestionAnsweringEngine = Depends(get_qa_engine)
):
    """
    Answer multiple questions in a single request.
    
    Efficient batch processing for multiple related questions.
    """
    try:
        start_time = time.time()
        
        # Determine index to search
        if request.index == "pubmed":
            index_name = "pubmed_articles"
        elif request.index == "clinical_trials":
            index_name = "clinical_trials"
        else:  # both
            index_name = "all"
        
        logger.info(f"Processing {len(request.questions)} questions in batch")
        
        # Process each question
        results = []
        for question in request.questions:
            question_start = time.time()
            
            result = qa_engine.answer_question(
                question=question,
                index_name=index_name,
                num_answers=request.max_answers_per_question
            )
            
            # Convert to response format
            answers = [
                AnswerResult(
                    answer=ans["answer"],
                    confidence=ans["confidence"],
                    confidence_level=ans["confidence_level"],
                    source_title=ans["title"],
                    source_id=ans["doc_id"],
                    source_type=ans["source_type"],
                    section=ans["section"],
                    context=ans.get("context")
                )
                for ans in result.get("answers", [])
            ]
            
            passages = [
                PassageResult(
                    text=(passage.get("text") or "")[:500],
                    score=passage.get("score") or 0.0,
                    source_title=passage.get("title") or "No Title",
                    source_id=passage.get("doc_id") or "unknown",
                    section=passage.get("section") or "abstract"
                )
                for passage in result.get("passages", [])
            ]
            
            question_time_ms = (time.time() - question_start) * 1000
            
            results.append(QuestionResponse(
                question=question,
                status=result["status"],
                answers=answers,
                passages=passages,
                qa_time_ms=round(question_time_ms, 2)
            ))
        
        total_time_ms = (time.time() - start_time) * 1000
        
        return BatchQuestionResponse(
            results=results,
            total_time_ms=round(total_time_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Batch question answering failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch question answering failed: {str(e)}")


@router.get("/document/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    index: str = Query(..., description="Index name: 'pubmed_articles' or 'clinical_trials'"),
    include_embedding: bool = Query(False, description="Include embedding vector in response"),
    search_engine: HybridSearchEngine = Depends(get_search_engine)
):
    """
    Retrieve a specific document by ID.
    
    Returns full document details including metadata and optionally the embedding vector.
    """
    try:
        logger.info(f"Retrieving document {document_id} from {index}")
        
        # Get document from Elasticsearch
        doc = search_engine.es_client.client.get(index=index, id=document_id)
        
        source = doc["_source"]
        source_type = "pubmed" if index == "pubmed_articles" else "clinical_trials"
        
        # Build full text from sections
        full_text_sections = []
        if source.get("abstract"):
            full_text_sections.append(source["abstract"])
        
        for key, value in source.items():
            if key.startswith("full_text_") and value:
                full_text_sections.append(value)
        
        full_text = "\n\n".join(full_text_sections) if full_text_sections else None
        
        response = DocumentResponse(
            id=document_id,
            title=source.get("title") or "No Title",
            abstract=source.get("abstract"),
            full_text=full_text,
            source=source_type,
            metadata={
                "authors": source.get("authors", []),
                # For clinical trials, fallback to start_date if publication_date not available
                "publication_date": source.get("publication_date") or source.get("publication_year") or source.get("year") or source.get("start_date") or "N/A",
                "journal": source.get("journal") or "N/A",
                "pmid": source.get("pmid"),
                "nct_id": source.get("nct_id"),
                "study_type": source.get("study_type"),
                "conditions": source.get("conditions", []),
                "interventions": source.get("interventions", [])
            }
        )
        
        if include_embedding and "embedding" in source:
            response.embedding = source["embedding"]
        
        return response
        
    except Exception as e:
        logger.error(f"Document retrieval failed: {e}")
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")


@router.get("/statistics")
async def get_statistics(
    search_engine: HybridSearchEngine = Depends(get_search_engine)
):
    """
    Get index statistics.
    
    Returns document counts and index information.
    """
    try:
        stats = {}
        
        for index_name in ["pubmed_articles", "clinical_trials"]:
            try:
                count = search_engine.es_client.client.count(index=index_name)
                stats[index_name] = {
                    "document_count": count["count"],
                    "index_exists": True
                }
            except Exception as e:
                stats[index_name] = {
                    "document_count": 0,
                    "index_exists": False,
                    "error": str(e)
                }
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")


@router.post("/document", response_model=IngestResponse)
async def add_document(
    request: DocumentIngestRequest,
    indexer: DocumentIndexer = Depends(get_document_indexer)
):
    """
    Add a new document to the specified index.
    """
    try:
        success = indexer.index_document(
            index_name=request.index,
            document=request.document,
            doc_id=request.doc_id
        )
        
        if success:
            return IngestResponse(
                status="success",
                message=f"Document indexed successfully in {request.index}",
                count=1
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to index document")
            
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/batch", response_model=IngestResponse)
async def add_documents_batch(
    request: BatchDocumentIngestRequest,
    indexer: DocumentIndexer = Depends(get_document_indexer)
):
    """
    Add multiple documents to the specified index in a batch.
    """
    try:
        success_count, failed_count = indexer.index_batch(
            index_name=request.index,
            documents=request.documents
        )
        
        return IngestResponse(
            status="success" if failed_count == 0 else "partial_success",
            message=f"Batch indexing complete: {success_count} successful, {failed_count} failed",
            count=success_count
        )
            
    except Exception as e:
        logger.error(f"Batch document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def init_maverick_db():
    try:
        conn = sqlite3.connect(MAVERICK_DB)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (user_id INTEGER, role TEXT, content TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize Maverick DB: {e}")

@router.get("/maverick/history")
async def get_maverick_history(user_id: int = Query(default=123, description="Telegram user ID")):
    """
    Sycnronize chat history from Maverick Telegram bot database.
    """
    init_maverick_db()
    
    try:
        conn = sqlite3.connect(MAVERICK_DB)
        c = conn.cursor()
        
        # Debug: Get table info
        c.execute("SELECT COUNT(*) FROM history")
        total_count = c.fetchone()[0]
        
        # Get history for specific user
        c.execute("SELECT role, content, timestamp, user_id FROM history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = c.fetchall()
        
        # Get last 5 overall for debug
        c.execute("SELECT role, content, user_id FROM history ORDER BY timestamp DESC LIMIT 5")
        recent_all = [{"role": r, "content": c, "uid": uid} for r, c, uid in c.fetchall()]
        
        conn.close()
        
        history = [{"role": r, "content": c, "timestamp": ts} for r, c, ts, uid in rows]
        return {
            "history": history, 
            "status": "success", 
            "debug": {
                "db_path": MAVERICK_DB,
                "total_records": total_count,
                "recent_overall": recent_all,
                "queried_user_id": user_id
            }
        }
    except Exception as e:
        return {"history": [], "status": "error", "message": str(e)}

@router.post("/maverick/chat")
async def maverick_chat(
    request: QuestionRequest,
    qa_engine: QuestionAnsweringEngine = Depends(get_qa_engine),
    settings: Settings = Depends(get_settings)
):
    """
    Conversational endpoint that syncs with Maverick's long-term memory.
    """
    user_id = 123 # Default sync ID for web user
    query = request.question
    
    init_maverick_db()
    
    try:
        # 1. Save user message to sync DB
        conn = sqlite3.connect(MAVERICK_DB)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, 'user', ?)", (user_id, query))
        conn.commit()
        
        # 2. Get answer (using existing RAG engine or Maverick logic)
        # We can use the qa_engine but style it as Maverick 🦞
        result = qa_engine.answer_question(question=query, num_answers=1)
        
        if result["status"] == "success" and result["answers"]:
            answer = result["answers"][0]["answer"]
            # Add Maverick personality if not already there
            if "🦞" not in answer:
                answer = "🦞 " + answer
        else:
            answer = "I'm sorry, I couldn't find a precise answer in the literature. Rephrase your question? 🦞"
            
        # 3. Save assistant message to sync DB
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, 'assistant', ?)", (user_id, answer))
        conn.commit()
        conn.close()
        
        return {
            "answer": answer,
            "status": "success",
            "sources": result.get("answers", [])
        }
        
    except Exception as e:
        logger.error(f"Maverick sync chat failed: {e}")
        return {"answer": f"Error syncing with Maverick: {str(e)}", "status": "error"}
