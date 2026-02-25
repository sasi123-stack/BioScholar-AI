package com.biomedscholar.ai.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.biomedscholar.ai.data.api.RetrofitClient
import com.biomedscholar.ai.data.models.ChatTurn
import com.biomedscholar.ai.data.models.ChatRequest
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class ChatMessage(
    val role: String, // "user" or "ai"
    val content: String,
    val isLoading: Boolean = false
)

class ChatViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<ChatMessage>>(emptyList())
    val messages: StateFlow<List<ChatMessage>> = _messages

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _isOnline = MutableStateFlow(false)
    val isOnline: StateFlow<Boolean> = _isOnline

    init { checkHealth() }

    fun checkHealth() {
        viewModelScope.launch {
            try {
                RetrofitClient.maverickApi.getHealth()
                _isOnline.value = true
            } catch (e: Exception) {
                _isOnline.value = false
            }
        }
    }

    fun sendMessage(input: String) {
        if (input.isBlank()) return
        val userMsg = ChatMessage(role = "user", content = input)
        _messages.value = _messages.value + userMsg
        _isLoading.value = true

        viewModelScope.launch {
            try {
                val history = _messages.value
                    .filter { !it.isLoading }
                    .map { ChatTurn(role = if (it.role == "ai") "assistant" else it.role, content = it.content) }

                val response = RetrofitClient.maverickApi.chat(
                    ChatRequest(question = input, context = history.takeLast(10))
                )
                val aiMsg = ChatMessage(role = "ai", content = response.answer)
                _messages.value = _messages.value + aiMsg
            } catch (e: Exception) {
                val errMsg = ChatMessage(role = "ai", content = "💠 Connection error. Please check your network or try again.")
                _messages.value = _messages.value + errMsg
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun clearChat() { _messages.value = emptyList() }
}
