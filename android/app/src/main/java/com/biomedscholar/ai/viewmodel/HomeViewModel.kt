package com.biomedscholar.ai.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.biomedscholar.ai.data.api.RetrofitClient
import com.biomedscholar.ai.data.models.Article
import com.biomedscholar.ai.data.models.SearchRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class HomeViewModel : ViewModel() {
    private val _articles = MutableStateFlow<List<Article>>(emptyList())
    val articles: StateFlow<List<Article>> = _articles

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    private val _bookmarks = MutableStateFlow<Set<String>>(emptySet())
    val bookmarks: StateFlow<Set<String>> = _bookmarks

    fun search(query: String, sourceFilter: String = "both") {
        if (query.isBlank()) return
        _isLoading.value = true
        _error.value = null

        viewModelScope.launch {
            try {
                // Map frontend filter labels to backend index names
                val indexName = when (sourceFilter) {
                    "PubMed" -> "pubmed"
                    "Clinical Trials" -> "clinical_trials"
                    else -> "both"
                }

                val request = SearchRequest(
                    query = query,
                    index = indexName,
                    max_results = 25
                )
                
                val response = RetrofitClient.maverickApi.search(request)
                
                // Convert backend results to Article objects and refine fields
                _articles.value = response.results.map { doc ->
                    val year = (doc.metadata["publication_date"] as? String)?.take(4) 
                               ?: (doc.metadata["publication_year"] as? String)?.take(4) 
                               ?: doc.year.take(4)
                    
                    Article(
                        id = doc.id,
                        title = doc.title,
                        authors = (doc.metadata["authors"] as? List<*>)?.joinToString(", ") ?: doc.authors,
                        journal = doc.metadata["journal"] as? String ?: doc.journal,
                        year = year,
                        abstract = doc.abstract,
                        source = doc.source,
                        score = doc.score,
                        metadata = doc.metadata
                    )
                }
            } catch (e: Exception) {
                _error.value = "Search failed: ${e.message}"
                _articles.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun toggleBookmark(articleId: String) {
        _bookmarks.value = if (_bookmarks.value.contains(articleId))
            _bookmarks.value - articleId else _bookmarks.value + articleId
    }

    fun isBookmarked(articleId: String) = _bookmarks.value.contains(articleId)

    fun clearResults() { _articles.value = emptyList() }
}
