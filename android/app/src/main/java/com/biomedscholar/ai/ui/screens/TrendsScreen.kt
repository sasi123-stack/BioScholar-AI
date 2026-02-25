package com.biomedscholar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.biomedscholar.ai.ui.theme.PrimaryBlue

data class TrendItem(val label: String, val growth: String)
data class VolumeData(val year: String, val count: Int)

val emergingTopics = listOf(
    TrendItem("GLP-1 Agonists", "+245%"),
    TrendItem("CRISPR-Cas9 Editing", "+182%"),
    TrendItem("mRNA Immunotherapy", "+134%"),
    TrendItem("AI in Radiology", "+115%")
)

val highVolumeTopics = listOf("Type 2 Diabetes","Breast Cancer","COVID-19","Hypertension","Alzheimer's","Depression")

val volumeData = listOf(
    VolumeData("2020", 3200), VolumeData("2021", 3800),
    VolumeData("2022", 4100), VolumeData("2023", 4500),
    VolumeData("2024", 5100), VolumeData("2025", 5800),
    VolumeData("2026", 2400)
)

@Composable
fun TrendsScreen(paddingValues: PaddingValues) {
    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .padding(bottom = paddingValues.calculateBottomPadding()),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Column {
                Text("Macro Research Trends", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.W700)
                Text("Live analysis of biomedical publication volumes and emerging focal areas.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
            }
        }

        // Fast-Emerging Topics
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = PrimaryBlue)
            ) {
                Column(Modifier.padding(16.dp)) {
                    Text("🔥  Fast-Emerging Topics", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.W700, color = Color.White)
                    Spacer(Modifier.height(12.dp))
                    emergingTopics.forEach { item ->
                        Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(item.label, style = MaterialTheme.typography.bodyMedium, color = Color.White)
                            Text(item.growth, style = MaterialTheme.typography.labelLarge, color = Color(0xFFBBF7D0), fontWeight = FontWeight.W700)
                        }
                        if (item != emergingTopics.last()) HorizontalDivider(color = Color.White.copy(alpha = 0.2f))
                    }
                }
            }
        }

        // Highest Volume Topics
        item {
            Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(16.dp)) {
                    Text("📚  Highest Volume (All-Time)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.W600)
                    Spacer(Modifier.height(12.dp))
                    @OptIn(ExperimentalLayoutApi::class)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        highVolumeTopics.forEach { topic ->
                            SuggestionChip(onClick = {}, label = { Text(topic) },
                                shape = RoundedCornerShape(999.dp)
                            )
                        }
                    }
                }
            }
        }

        // Publication Volume Chart
        item {
            Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(16.dp)) {
                    Text("Publication Volume by Year", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.W600)
                    Spacer(Modifier.height(16.dp))
                    // Simple bar chart using Box composables
                    val maxVal = volumeData.maxOf { it.count }.toFloat()
                    Row(Modifier.fillMaxWidth().height(150.dp), verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        volumeData.forEach { data ->
                            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                                Box(
                                    Modifier
                                        .fillMaxWidth()
                                        .fillMaxHeight(data.count / maxVal)
                                        .background(PrimaryBlue, RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp))
                                )
                            }
                        }
                    }
                    Spacer(Modifier.height(6.dp))
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        volumeData.forEach { data ->
                            Text(data.year, style = MaterialTheme.typography.labelMedium, fontSize = com.biomedscholar.ai.ui.theme.AppTypography.labelMedium.fontSize * 0.7f, modifier = Modifier.weight(1f), color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f), maxLines = 1)
                        }
                    }
                }
            }
        }
        
        item {
            Spacer(Modifier.height(48.dp))
        }
    }
}
