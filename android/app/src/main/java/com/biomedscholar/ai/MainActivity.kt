package com.biomedscholar.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.*
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import com.biomedscholar.ai.ui.navigation.AppNavigation
import com.biomedscholar.ai.ui.theme.BioMedScholarTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // Install splash screen BEFORE super.onCreate
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)

        enableEdgeToEdge()

        setContent {
            var darkTheme by remember { mutableStateOf(false) }

            BioMedScholarTheme(darkTheme = darkTheme) {
                AppNavigation(
                    darkTheme = darkTheme,
                    onToggleDark = { darkTheme = !darkTheme }
                )
            }
        }
    }
}
