package com.biomedscholar.ai.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.biomedscholar.ai.ui.theme.PrimaryBlue
import com.biomedscholar.ai.viewmodel.ChatMessage
import com.biomedscholar.ai.viewmodel.ChatViewModel
import de.charlex.compose.HtmlText

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(
    viewModel: ChatViewModel,
    paddingValues: PaddingValues
) {
    val messages by viewModel.messages.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val isOnline by viewModel.isOnline.collectAsState()
    var inputText by remember { mutableStateOf("") }
    val listState = rememberLazyListState()

    LaunchedEffect(messages.size) {
        if (messages.isNotEmpty()) listState.animateScrollToItem(messages.size - 1)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .padding(bottom = paddingValues.calculateBottomPadding())
    ) {
        // Top bar
        Surface(shadowElevation = 2.dp) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(Icons.Default.Science, contentDescription = null, tint = PrimaryBlue, modifier = Modifier.size(32.dp))
                Spacer(Modifier.width(12.dp))
                Column {
                    Text("Maverick Research AI", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.W600)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            Modifier.size(7.dp).background(
                                if (isOnline) Color(0xFF10B981) else Color(0xFFEF4444),
                                shape = RoundedCornerShape(999.dp)
                            )
                        )
                        Spacer(Modifier.width(5.dp))
                        Text(
                            if (isOnline) "Connected to Secure Research Node" else "Reconnecting…",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                        )
                    }
                }
                Spacer(Modifier.weight(1f))
                IconButton(onClick = { viewModel.clearChat() }) {
                    Icon(Icons.Default.Delete, contentDescription = "Clear")
                }
            }
        }

        // Messages
        LazyColumn(
            state = listState,
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Welcome message if empty
            if (messages.isEmpty()) {
                item {
                    WelcomeMessage()
                }
            }

            items(messages) { msg -> ChatBubble(msg) }

            if (isLoading) {
                item { ThinkingIndicator() }
            }
            
            item {
                Spacer(Modifier.height(32.dp))
            }
        }

        // Input area
        Surface(shadowElevation = 8.dp) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 10.dp)
                    .navigationBarsPadding(),
                verticalAlignment = Alignment.Bottom
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    modifier = Modifier.weight(1f),
                    placeholder = { Text("Ask Maverick about biomedical research…", fontSize = 14.sp) },
                    shape = RoundedCornerShape(24.dp),
                    maxLines = 4,
                    colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = PrimaryBlue)
                )
                Spacer(Modifier.width(8.dp))
                IconButton(
                    onClick = {
                        if (inputText.isNotBlank()) {
                            viewModel.sendMessage(inputText.trim())
                            inputText = ""
                        }
                    },
                    enabled = !isLoading && inputText.isNotBlank(),
                    modifier = Modifier.size(48.dp).background(PrimaryBlue, RoundedCornerShape(999.dp))
                ) {
                    Icon(Icons.Default.Send, contentDescription = "Send", tint = Color.White)
                }
            }
        }
    }
}

@Composable
fun ChatBubble(msg: ChatMessage) {
    val isUser = msg.role == "user"
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        if (!isUser) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .background(PrimaryBlue, RoundedCornerShape(999.dp)),
                contentAlignment = Alignment.Center
            ) {
                Text("💠", fontSize = 14.sp)
            }
            Spacer(Modifier.width(8.dp))
        }
        Surface(
            shape = RoundedCornerShape(
                topStart = if (isUser) 16.dp else 4.dp,
                topEnd = 16.dp,
                bottomStart = 16.dp,
                bottomEnd = if (isUser) 4.dp else 16.dp
            ),
            color = if (isUser) PrimaryBlue else MaterialTheme.colorScheme.surface,
            shadowElevation = if (isUser) 0.dp else 1.dp,
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            if (isUser) {
                Text(
                    text = msg.content,
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                    color = Color.White,
                    style = MaterialTheme.typography.bodyMedium,
                    lineHeight = 22.sp
                )
            } else {
                HtmlText(
                    text = msg.content,
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                    style = MaterialTheme.typography.bodyMedium.copy(
                        color = MaterialTheme.colorScheme.onSurface,
                        lineHeight = 22.sp
                    )
                )
            }
        }
    }
}

@Composable
fun ThinkingIndicator() {
    Row(verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(32.dp).background(PrimaryBlue, RoundedCornerShape(999.dp)), Alignment.Center) {
            Text("💠", fontSize = 14.sp)
        }
        Spacer(Modifier.width(8.dp))
        Surface(shape = RoundedCornerShape(4.dp, 16.dp, 16.dp, 16.dp), color = MaterialTheme.colorScheme.surface, shadowElevation = 1.dp) {
            Row(Modifier.padding(horizontal = 14.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                CircularProgressIndicator(modifier = Modifier.size(16.dp), strokeWidth = 2.dp, color = PrimaryBlue)
                Spacer(Modifier.width(8.dp))
                Text("💠 Maverick Suite Thinking…", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f))
            }
        }
    }
}

@Composable
fun WelcomeMessage() {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(top = 80.dp, bottom = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text("💠", fontSize = 64.sp)
        Spacer(Modifier.height(16.dp))
        Text("Maverick Research AI", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.W700)
        Spacer(Modifier.height(10.dp))
        Text(
            text = "Specialized in medicine, oncology & pharmacology.\nAsk me anything about biomedical research.",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center,
            lineHeight = 24.sp
        )
    }
}
