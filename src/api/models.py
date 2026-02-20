"""
Pydantic models for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request model for search endpoint."""
    
    query: str = Field(..., description="Search query string", min_length=1)
    index: Optional[str] = Field("both", description="Index to search: 'pubmed', 'clinical_trials', or 'both'")
    max_results: Optional[int] = Field(50, description="Maximum number of results", ge=1, le=100)
    alpha: Optional[float] = Field(0.5, description="Weight for hybrid search (0=keyword only, 1=semantic only)", ge=0.0, le=1.0)
    use_reranking: Optional[bool] = Field(True, description="Whether to apply cross-encoder reranking")
    sort_by: Optional[str] = Field("relevance", description="Sort criteria: 'relevance', 'date_desc', 'date_asc'")
    date_from: Optional[int] = Field(None, description="Start year filter")
    date_to: Optional[int] = Field(None, description="End year filter")
    article_types: Optional[List[str]] = Field(default_factory=list, description="List of article types to filter by")
    subject: Optional[str] = Field(None, description="Subject filter (human, animal, etc.)")
    availability: Optional[str] = Field(None, description="Availability filter (abstract, full_text, open_access)")


class DocumentResult(BaseModel):
    """Model for a single document result."""
    
    id: str = Field(..., description="Document ID")
    title: str = Field("No Title", description="Document title")
    abstract: Optional[str] = Field(None, description="Document abstract")
    score: float = Field(0.0, description="Relevance score")
    source: str = Field("unknown", description="Source: 'pubmed' or 'clinical_trials'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class SearchResponse(BaseModel):
    """Response model for search endpoint."""
    
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total number of results found")
    results: List[DocumentResult] = Field(default_factory=list, description="Search results")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")


class QuestionRequest(BaseModel):
    """Request model for question answering endpoint."""
    
    question: str = Field(..., description="Question to answer", min_length=1)
    max_answers: Optional[int] = Field(1, description="Maximum number of answers to return", ge=1, le=10)
    min_confidence: Optional[float] = Field(0.01, description="Minimum confidence threshold", ge=0.0, le=1.0)
    index: Optional[str] = Field("both", description="Index to search: 'pubmed', 'clinical_trials', or 'both'")
    max_passages: Optional[int] = Field(5, description="Maximum passages to extract", ge=1, le=20)


class AnswerResult(BaseModel):
    """Model for a single answer result."""
    
    answer: str = Field(..., description="Extracted answer text")
    confidence: float = Field(0.0, description="Confidence score")
    confidence_level: str = Field("low", description="Confidence level: high/medium/low/very_low")
    source_title: str = Field("No Title", description="Source document title")
    source_id: str = Field("unknown", description="Source document ID")
    source_type: str = Field("unknown", description="Source type: 'pubmed' or 'clinical_trials'")
    section: str = Field("abstract", description="Document section containing the answer")
    context: Optional[str] = Field(None, description="Surrounding context")
    journal: Optional[str] = Field(None, description="Journal name or source")
    publication_date: Optional[str] = Field(None, description="Publication date")


class PassageResult(BaseModel):
    """Model for a retrieved passage."""
    
    text: str = Field("", description="Passage text")
    score: float = Field(0.0, description="Relevance score")
    source_title: str = Field("No Title", description="Source document title")
    source_id: str = Field("unknown", description="Source document ID")
    section: str = Field("abstract", description="Document section")


class QuestionResponse(BaseModel):
    """Response model for question answering endpoint."""
    
    question: str = Field(..., description="Original question")
    status: str = Field(..., description="Status: 'success' or 'no_answer'")
    answers: List[AnswerResult] = Field(default_factory=list, description="Extracted answers")
    passages: List[PassageResult] = Field(default_factory=list, description="Retrieved passages")
    qa_time_ms: float = Field(..., description="QA execution time in milliseconds")


class DocumentResponse(BaseModel):
    """Response model for document retrieval endpoint."""
    
    id: str = Field(..., description="Document ID")
    title: str = Field(..., description="Document title")
    abstract: Optional[str] = Field(None, description="Document abstract")
    full_text: Optional[str] = Field(None, description="Full text if available")
    source: str = Field(..., description="Source: 'pubmed' or 'clinical_trials'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    embedding: Optional[List[float]] = Field(None, description="Document embedding vector")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Service status")
    elasticsearch: bool = Field(..., description="Elasticsearch connection status")
    models_loaded: bool = Field(..., description="ML models loaded status")
    version: str = Field(..., description="API version")
    features: Optional[Dict[str, bool]] = Field(None, description="Feature availability flags")


class BatchQuestionRequest(BaseModel):
    """Request model for batch question answering."""
    
    questions: List[str] = Field(..., description="List of questions to answer", min_items=1, max_items=10)
    index: Optional[str] = Field("both", description="Index to search: 'pubmed', 'clinical_trials', or 'both'")
    max_answers_per_question: Optional[int] = Field(1, description="Max answers per question", ge=1, le=5)
    min_confidence: Optional[float] = Field(0.01, description="Minimum confidence threshold", ge=0.0, le=1.0)


class BatchQuestionResponse(BaseModel):
    """Response model for batch question answering."""
    
    results: List[QuestionResponse] = Field(..., description="QA results for each question")
    total_time_ms: float = Field(..., description="Total execution time in milliseconds")


class DocumentIngestRequest(BaseModel):
    """Request model for indexing a document."""
    
    index: str = Field(..., description="Index name: 'pubmed_articles' or 'clinical_trials'")
    document: Dict[str, Any] = Field(..., description="Document content to index")
    doc_id: Optional[str] = Field(None, description="Optional document ID")


class BatchDocumentIngestRequest(BaseModel):
    """Request model for indexing multiple documents."""
    
    index: str = Field(..., description="Index name: 'pubmed_articles' or 'clinical_trials'")
    documents: List[Dict[str, Any]] = Field(..., description="List of documents to index")


class IngestResponse(BaseModel):
    """Response model for ingestion endpoints."""
    
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Details about the operation")
    count: Optional[int] = Field(None, description="Number of documents processed")
