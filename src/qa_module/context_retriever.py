"""Context retriever for QA system."""

from typing import List, Dict, Optional
from src.search_engine import HybridSearchEngine
from src.utils.logger import get_logger
from src.utils.web_search import WebSearchTool

logger = get_logger(__name__)


class ContextRetriever:
    """Retrieve relevant context passages for question answering."""
    
    def __init__(
        self,
        search_engine: Optional[HybridSearchEngine] = None,
        web_search_tool: Optional[WebSearchTool] = None,
        max_passages: int = 5,
        passage_length: int = 512
    ):
        """Initialize context retriever.
        
        Args:
            search_engine: Search engine for retrieving documents
            web_search_tool: Tool for internet searching
            max_passages: Maximum number of passages to retrieve
            passage_length: Maximum length of each passage (characters)
        """
        self.search_engine = search_engine or HybridSearchEngine()
        self.web_search_tool = web_search_tool or WebSearchTool()
        self.max_passages = max_passages
        self.passage_length = passage_length
        
        logger.info(f"ContextRetriever initialized (max_passages={max_passages})")
    
    def retrieve_from_documents(
        self,
        question: str,
        documents: List[Dict],
        top_k: int = None
    ) -> List[Dict]:
        """Extract relevant passages from provided documents.
        
        Args:
            question: User question
            documents: List of documents to extract from
            top_k: Number of passages to return
            
        Returns:
            List of passage dictionaries with text and metadata
        """
        top_k = top_k or self.max_passages
        passages = []
        
        for doc in documents:
            source = doc.get('source', {})
            
            # Extract text fields
            title = source.get('title', '')
            abstract = source.get('abstract', '')
            full_text = source.get('full_text', '')
            
            # Derive source type if missing
            source_type = source.get('source')
            if not source_type:
                if "pmid" in source or "pubmed" in str(doc.get('id', '')).lower():
                    source_type = "pubmed"
                elif "nct_id" in source or "nct" in str(doc.get('id', '')).lower():
                    source_type = "clinical_trials"
                else:
                    source_type = "unknown"
            
            # Create passages from different sections
            if abstract:
                passages.append({
                    'text': abstract[:self.passage_length],
                    'title': title,
                    'doc_id': doc.get('id'),
                    'source_type': source_type,
                    'section': 'abstract',
                    'score': doc.get('score', 0.0),
                    'journal': source.get('journal'),
                    'publication_date': source.get('publication_date') or source.get('start_date')
                })
            
            if full_text and len(full_text) > len(abstract):
                # Split full text into chunks
                chunks = self._chunk_text(full_text, self.passage_length)
                for i, chunk in enumerate(chunks[:3]):  # Max 3 chunks per doc
                    passages.append({
                        'text': chunk,
                        'title': title,
                        'doc_id': doc.get('id'),
                        'source_type': source_type,
                        'section': f'full_text_{i+1}',
                        'score': doc.get('score', 0.0) * 0.8,  # Slightly lower score for full text
                        'journal': source.get('journal'),
                        'publication_date': source.get('publication_date') or source.get('start_date')
                    })
        
        # Sort by score and return top k
        passages.sort(key=lambda x: x['score'], reverse=True)
        
        return passages[:top_k]
    
    def retrieve_for_question(
        self,
        question: str,
        index_name: str = 'pubmed_articles',
        top_k: int = None
    ) -> List[Dict]:
        """Retrieve relevant passages for a question (Synchronous)."""
        import asyncio
        try:
            # Try to run in current loop if exists, else create new
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # This is tricky in FastAPI, but for now we'll try a wrapper
                # or just use the async version
                return asyncio.run_coroutine_threadsafe(
                    self.retrieve_for_question_async(question, index_name, top_k),
                    loop
                ).result()
            else:
                return loop.run_until_complete(self.retrieve_for_question_async(question, index_name, top_k))
        except Exception:
            return asyncio.run(self.retrieve_for_question_async(question, index_name, top_k))

    async def retrieve_for_question_async(
        self,
        question: str,
        index_name: str = 'pubmed_articles',
        top_k: int = None
    ) -> List[Dict]:
        """Retrieve relevant passages for a question (Asynchronous).
        
        Args:
            question: User question
            index_name: Index to search (pubmed_articles, clinical_trials, all, google)
            top_k: Number of passages to return
            
        Returns:
            List of passage dictionaries
        """
        top_k = top_k or self.max_passages
        
        logger.info(f"Retrieving context for: '{question}' in {index_name}")
        documents = []
        
        # Search for relevant documents
        if index_name == 'pubmed_articles':
            documents = self.search_engine.search_pubmed(question, size=10)
        elif index_name == 'clinical_trials':
            documents = self.search_engine.search_clinical_trials(question, size=10)
        elif index_name == 'google':
            web_results = await self.web_search_tool.search(question, num_results=10)
            for i, res in enumerate(web_results):
                documents.append({
                    'id': f"web-{i}",
                    'score': 1.0 - (i * 0.05),
                    'source': {
                        'title': res['title'],
                        'abstract': res['snippet'],
                        'link': res['link'],
                        'source': 'google'
                    }
                })
        else:  # 'all' or any other value
            # Search primary indices
            results = self.search_engine.search_all(question, size=5)
            documents = results['pubmed'] + results['clinical_trials']
            
            # Optionally add internet if no medical results found or if explicitly 'all'
            if not documents or index_name == 'all':
                web_results = await self.web_search_tool.search(question, num_results=5)
                for i, res in enumerate(web_results):
                    documents.append({
                        'id': f"web-{i}",
                        'score': 0.8 - (i * 0.05), # Lower score priority than peer-reviewed
                        'source': {
                            'title': res['title'],
                            'abstract': res['snippet'],
                            'link': res['link'],
                            'source': 'google'
                        }
                    })
        
        logger.info(f"Found {len(documents)} relevant documents/links")
        
        # Extract passages
        passages = self.retrieve_from_documents(question, documents, top_k)
        
        logger.info(f"Extracted {len(passages)} passages")
        
        return passages
    
    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into chunks.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def format_context(self, passages: List[Dict]) -> str:
        """Format passages into single context string.
        
        Args:
            passages: List of passage dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, passage in enumerate(passages, 1):
            title = passage.get('title', 'Untitled')
            text = passage.get('text', '')
            section = passage.get('section', '')
            
            context_parts.append(f"[Passage {i} - {title} ({section})]")
            context_parts.append(text)
            context_parts.append("")  # Empty line
        
        return "\n".join(context_parts)
    
    def close(self):
        """Close connections."""
        if self.search_engine:
            self.search_engine.close()
