package com.biomedscholar.ai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.biomedscholar.ai.data.models.Article
import com.biomedscholar.ai.ui.theme.PrimaryBlue

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ArticleDetailScreen(
    article: Article,
    onBack: () -> Unit,
    onAskMaverick: () -> Unit
) {
    val scrollState = rememberScrollState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Article Detail") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.surface)
            )
        },
        bottomBar = {
            Surface(shadowElevation = 8.dp) {
                Button(
                    onClick = onAskMaverick,
                    modifier = Modifier.fillMaxWidth().padding(16.dp),
                    shape = RoundedCornerShape(999.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue)
                ) {
                    Text("💠  Ask Maverick About This Article", fontWeight = FontWeight.W600)
                }
            }
        }
    ) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(scrollState)
                .padding(horizontal = 20.dp, vertical = 16.dp)
        ) {
            // Source badge + year
            Row(verticalAlignment = Alignment.CenterVertically) {
                com.biomedscholar.ai.ui.components.SourceBadge(type = article.source)
                Spacer(Modifier.width(8.dp))
                if (article.year.isNotEmpty()) {
                    Text(article.year, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                }
            }

            Spacer(Modifier.height(16.dp))

            // Title
            Text(article.title, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.W700, lineHeight = MaterialTheme.typography.headlineMedium.lineHeight)

            Spacer(Modifier.height(16.dp))

            // Authors
            if (article.authors.isNotEmpty()) {
                Text("Authors", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                Text(article.authors, style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(10.dp))
            }

            // Journal
            if (article.journal.isNotEmpty()) {
                Text("Journal", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f))
                Text(article.journal, style = MaterialTheme.typography.bodyMedium, color = PrimaryBlue, fontWeight = FontWeight.W500)
                Spacer(Modifier.height(16.dp))
            }

            HorizontalDivider()
            Spacer(Modifier.height(16.dp))

            // Abstract
            Text("Abstract", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.W700)
            Spacer(Modifier.height(8.dp))
            Text(
                text = article.abstract?.ifEmpty { "Abstract not available. Open source to view the full article." } ?: "Abstract not available.",
                style = MaterialTheme.typography.bodyLarge,
                lineHeight = MaterialTheme.typography.bodyLarge.lineHeight,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.85f)
            )

            Spacer(Modifier.height(24.dp))

            // Action buttons
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                OutlinedButton(onClick = {}, shape = RoundedCornerShape(999.dp)) {
                    Icon(Icons.Default.FormatQuote, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Cite")
                }
                OutlinedButton(onClick = {}, shape = RoundedCornerShape(999.dp)) {
                    Icon(Icons.Default.Share, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("Share")
                }
                OutlinedButton(onClick = {}, shape = RoundedCornerShape(999.dp)) {
                    Icon(Icons.Default.Bookmark, contentDescription = null, modifier = Modifier.size(16.dp), tint = PrimaryBlue)
                    Spacer(Modifier.width(4.dp))
                    Text("Save")
                }
            }

            Spacer(Modifier.height(12.dp))

            // Open PubMed
            if (article.source == "pubmed") {
                TextButton(onClick = {}) {
                    Icon(Icons.Default.OpenInNew, contentDescription = null, modifier = Modifier.size(16.dp), tint = PrimaryBlue)
                    Spacer(Modifier.width(4.dp))
                    Text("Open in PubMed", color = PrimaryBlue)
                }
            } else if (article.source == "clinical_trials") {
                TextButton(onClick = {}) {
                    Icon(Icons.Default.OpenInNew, contentDescription = null, modifier = Modifier.size(16.dp), tint = PrimaryBlue)
                    Spacer(Modifier.width(4.dp))
                    Text("Open ClinicalTrials.gov", color = PrimaryBlue)
                }
            }

            Spacer(Modifier.height(80.dp))
        }
    }
}
