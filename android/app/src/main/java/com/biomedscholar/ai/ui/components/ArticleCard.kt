package com.biomedscholar.ai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.BookmarkBorder
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.biomedscholar.ai.data.models.Article
import com.biomedscholar.ai.ui.theme.*

@Composable
fun ArticleCard(
    article: Article,
    isBookmarked: Boolean,
    onCardClick: () -> Unit,
    onBookmark: () -> Unit,
    onAskMaverick: () -> Unit
) {
    val borderColor = MaterialTheme.colorScheme.outline
    val surfaceColor = MaterialTheme.colorScheme.surface

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clickable { onCardClick() },
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = surfaceColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(Modifier.padding(16.dp)) {
            // Source badge + year + bookmark
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                SourceBadge(type = article.source)
                Spacer(Modifier.weight(1f))
                if (article.year.isNotEmpty()) {
                    Text(
                        text = article.year,
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f)
                    )
                }
                Spacer(Modifier.width(8.dp))
                IconButton(onClick = onBookmark, modifier = Modifier.size(24.dp)) {
                    Icon(
                        imageVector = if (isBookmarked) Icons.Default.Bookmark else Icons.Default.BookmarkBorder,
                        contentDescription = "Bookmark",
                        tint = if (isBookmarked) PrimaryBlue else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            Spacer(Modifier.height(10.dp))

            // Title
            Text(
                text = article.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.W600,
                maxLines = 3,
                overflow = TextOverflow.Ellipsis,
                color = MaterialTheme.colorScheme.onSurface
            )

            Spacer(Modifier.height(6.dp))

            // Authors
            if (article.authors.isNotEmpty()) {
                Text(
                    text = article.authors,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
            }

            // Journal
            if (article.journal.isNotEmpty()) {
                Text(
                    text = article.journal,
                    style = MaterialTheme.typography.bodyMedium,
                    color = PrimaryBlue,
                    fontWeight = FontWeight.W500,
                    maxLines = 1
                )
            }

            // Abstract preview
            if (article.abstract?.isNotEmpty() == true) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = article.abstract!!,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis,
                    lineHeight = 20.sp
                )
            }

            Spacer(Modifier.height(12.dp))
            HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.4f))
            Spacer(Modifier.height(10.dp))

            // Action buttons
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(onClick = {}) {
                    Text("Cite", style = MaterialTheme.typography.labelLarge, color = TextMuted)
                }
                TextButton(onClick = {}) {
                    Icon(Icons.Default.Share, contentDescription = "Share", modifier = Modifier.size(14.dp), tint = TextMuted)
                    Spacer(Modifier.width(4.dp))
                    Text("Share", style = MaterialTheme.typography.labelLarge, color = TextMuted)
                }
                Spacer(Modifier.weight(1f))
                Button(
                    onClick = onAskMaverick,
                    colors = ButtonDefaults.buttonColors(containerColor = PrimaryBlue),
                    shape = RoundedCornerShape(999.dp),
                    contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                    modifier = Modifier.height(32.dp)
                ) {
                    Text("Ask Maverick →", style = MaterialTheme.typography.labelLarge, color = androidx.compose.ui.graphics.Color.White)
                }
            }
        }
    }
}

@Composable
fun SourceBadge(type: String) {
    val isPublished = type == "pubmed"
    val label = if (isPublished) "PubMed" else "Clinical Trial"
    val color = if (isPublished) PrimaryBlue else GoogleGreen

    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(color.copy(alpha = 0.1f))
            .border(1.dp, color.copy(alpha = 0.4f), RoundedCornerShape(999.dp))
            .padding(horizontal = 8.dp, vertical = 2.dp)
    ) {
        Text(label, style = MaterialTheme.typography.labelMedium, color = color)
    }
}
