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

    fun search(query: String, sourceFilter: String = "All Sources") {
        if (query.isBlank()) return
        _isLoading.value = true
        _error.value = null
        _articles.value = emptyList()

        viewModelScope.launch {
            try {
                val indexName = when (sourceFilter) {
                    "PubMed" -> "pubmed_articles"
                    "Clinical Trials" -> "clinical_trials"
                    else -> "both"
                }

                val request = SearchRequest(
                    query = query,
                    index = indexName,
                    max_results = 25
                )

                val response = RetrofitClient.maverickApi.search(request)

                _articles.value = response.results.map { doc ->
                    // authors can come back as a JSON array or a plain string
                    val authorsStr = when (val a = doc.authors) {
                        is List<*> -> a.joinToString(", ")
                        is String -> a
                        else -> doc.metadata["authors"]?.toString() ?: "Unknown Authors"
                    }

                    // year: prefer top-level field, fall back to metadata
                    val year = doc.year?.take(4)
                        ?: (doc.metadata["publication_date"] as? String)?.take(4)
                        ?: (doc.metadata["publication_year"] as? String)?.take(4)
                        ?: ""

                    val journal = doc.journal
                        ?: doc.metadata["journal"] as? String
                        ?: doc.metadata["source_name"] as? String
                        ?: "Biomedical Literature"

                    Article(
                        id = doc.id,
                        title = doc.title,
                        authors = authorsStr,
                        journal = journal,
                        year = year,
                        abstract = doc.abstract,
                        source = doc.source,
                        score = doc.score.toFloat(),
                        metadata = doc.metadata
                    )
                }

                if (_articles.value.isEmpty()) {
                    _error.value = "No results found for \"$query\". Try different keywords."
                }
            } catch (e: Exception) {
                _error.value = "Search failed: ${e.message ?: "Unknown error"}"
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

    fun clearResults() {
        _articles.value = emptyList()
        _error.value = null
    }
}
