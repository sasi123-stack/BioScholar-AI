package com.biomedscholar.ai.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColorScheme = lightColorScheme(
    primary = PrimaryBlue,
    onPrimary = Color.White,
    primaryContainer = PrimaryBlueLight,
    secondary = TextSecondary,
    background = BgSecondary,
    surface = BgPrimary,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    outline = BorderColor,
    error = GoogleRed
)

private val DarkColorScheme = darkColorScheme(
    primary = PrimaryBlue,
    onPrimary = Color.White,
    primaryContainer = Color(0xFF1E3A5F),
    secondary = DarkTextSecondary,
    background = DarkBgSecondary,
    surface = DarkBgPrimary,
    onBackground = DarkTextPrimary,
    onSurface = DarkTextPrimary,
    outline = DarkBorderColor,
    error = GoogleRed
)

@Composable
fun BioMedScholarTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
