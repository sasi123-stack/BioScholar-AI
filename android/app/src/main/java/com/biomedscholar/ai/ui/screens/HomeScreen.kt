package com.biomedscholar.ai.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.biomedscholar.ai.data.models.Article
import com.biomedscholar.ai.ui.components.ArticleCard
import com.biomedscholar.ai.ui.theme.PrimaryBlue
import com.biomedscholar.ai.viewmodel.HomeViewModel

val SOURCE_FILTERS = listOf("All Sources", "PubMed", "Clinical Trials", "Web Search")
val SUGGESTED_QUERIES = listOf("COVID-19 vaccines", "CRISPR therapy", "GLP-1 Agonists", "Breast cancer immunotherapy")

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    paddingValues: PaddingValues,
    darkTheme: Boolean,
    onToggleDark: () -> Unit,
    onArticleClick: (Article) -> Unit,
    onAskMaverick: (String) -> Unit
) {
    val articles by viewModel.articles.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val bookmarks by viewModel.bookmarks.collectAsState()

    var query by remember { mutableStateOf("") }
    var activeFilter by remember { mutableStateOf("All Sources") }
    val keyboard = LocalSoftwareKeyboardController.current

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Science, contentDescription = null, tint = PrimaryBlue, modifier = Modifier.size(28.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("BioMedScholar", fontWeight = FontWeight.W500, fontSize = 20.sp)
                        Text(" AI", color = PrimaryBlue, fontWeight = FontWeight.W700, fontSize = 20.sp)
                    }
                },
                actions = {
                    IconButton(onClick = onToggleDark) {
                        Icon(if (darkTheme) Icons.Default.LightMode else Icons.Default.DarkMode, contentDescription = "Toggle Dark Mode")
                    }
                    IconButton(onClick = {}) {
                        Icon(Icons.Default.Bookmarks, contentDescription = "Bookmarks")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { onAskMaverick(query) },
                containerColor = PrimaryBlue
            ) {
                Text("💠", fontSize = 22.sp)
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(bottom = paddingValues.calculateBottomPadding()),
            contentPadding = PaddingValues(bottom = 80.dp)
        ) {
            // Search bar
            item {
                Column(
                    Modifier
                        .fillMaxWidth()
                        .background(MaterialTheme.colorScheme.surface)
                        .padding(start = 16.dp, end = 16.dp, top = innerPadding.calculateTopPadding() + 12.dp, bottom = 12.dp)
                ) {
                    OutlinedTextField(
                        value = query,
                        onValueChange = { query = it },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("Search 35M+ biomedical papers…", color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f)) },
                        leadingIcon = { Icon(Icons.Default.Search, contentDescription = null, tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)) },
                        trailingIcon = {
                            Row {
                                if (query.isNotEmpty()) {
                                    IconButton(onClick = { query = ""; viewModel.clearResults() }) {
                                        Icon(Icons.Default.Clear, contentDescription = "Clear")
                                    }
                                }
                                IconButton(
                                    onClick = { viewModel.search(query, activeFilter); keyboard?.hide() },
                                    colors = IconButtonDefaults.iconButtonColors(containerColor = PrimaryBlue)
                                ) {
                                    Icon(Icons.Default.Search, contentDescription = "Search", tint = Color.White)
                                }
                            }
                        },
                        shape = RoundedCornerShape(999.dp),
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                        keyboardActions = KeyboardActions(onSearch = {
                            viewModel.search(query, activeFilter); keyboard?.hide()
                        }),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = PrimaryBlue,
                            unfocusedBorderColor = MaterialTheme.colorScheme.outline
                        )
                    )

                    Spacer(Modifier.height(10.dp))

                    // Filter chips
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(SOURCE_FILTERS) { filter ->
                            FilterChip(
                                selected = activeFilter == filter,
                                onClick = { activeFilter = filter },
                                label = { Text(filter, style = MaterialTheme.typography.labelLarge) },
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = PrimaryBlue,
                                    selectedLabelColor = Color.White
                                ),
                                shape = RoundedCornerShape(999.dp)
                            )
                        }
                    }
                }
                HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
            }

            // Loading state
            if (isLoading) {
                item {
                    Box(Modifier.fillMaxWidth().padding(48.dp), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            CircularProgressIndicator(color = PrimaryBlue)
                            Spacer(Modifier.height(16.dp))
                            Text("Searching biomedical literature…", color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                        }
                    }
                }
            }

            // Empty state with suggested queries
            if (!isLoading && articles.isEmpty()) {
                item {
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(Icons.Default.Search, contentDescription = null, modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.2f))
                        Spacer(Modifier.height(16.dp))
                        Text("Biomedical Research Intelligence", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.W600)
                        Spacer(Modifier.height(8.dp))
                        Text("Comprehensive access to 35M+ PubMed records and clinical trials", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
                        Spacer(Modifier.height(24.dp))
                        Text("Jump Start Your Research", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                        Spacer(Modifier.height(12.dp))
                        SUGGESTED_QUERIES.forEach { suggestion ->
                            SuggestionChip(
                                onClick = { query = suggestion; viewModel.search(suggestion) },
                                label = { Text(suggestion) },
                                modifier = Modifier.padding(vertical = 3.dp)
                            )
                        }
                    }
                }
            }

            // Results
            items(articles, key = { it.id }) { article ->
                ArticleCard(
                    article = article,
                    isBookmarked = bookmarks.contains(article.id),
                    onCardClick = { onArticleClick(article) },
                    onBookmark = { viewModel.toggleBookmark(article.id) },
                    onAskMaverick = { onAskMaverick(article.title) }
                )
            }
        }
    }
}
