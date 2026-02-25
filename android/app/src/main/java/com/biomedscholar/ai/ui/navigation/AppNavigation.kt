package com.biomedscholar.ai.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Science
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.biomedscholar.ai.data.models.Article
import com.biomedscholar.ai.ui.screens.*
import com.biomedscholar.ai.viewmodel.ChatViewModel
import com.biomedscholar.ai.viewmodel.HomeViewModel

sealed class Screen(val route: String, val label: String, val icon: ImageVector) {
    object Research : Screen("research", "Research", Icons.Default.Science)
    object Chat     : Screen("chat",     "AI Chat",  Icons.Default.Chat)
    object Trends   : Screen("trends",   "Trends",   Icons.Default.TrendingUp)
    object Login    : Screen("login",    "Login",    Icons.Default.Person)
}

val bottomNavItems = listOf(Screen.Research, Screen.Chat, Screen.Trends)

@Composable
fun AppNavigation(darkTheme: Boolean, onToggleDark: () -> Unit) {
    val navController = rememberNavController()
    val homeVm: HomeViewModel = viewModel()
    val chatVm: ChatViewModel = viewModel()

    var selectedArticle by remember { mutableStateOf<Article?>(null) }

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route
                bottomNavItems.forEach { screen ->
                    NavigationBarItem(
                        selected = currentRoute == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.startDestinationId) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(screen.icon, contentDescription = screen.label) },
                        label = { Text(screen.label) }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Login.route
        ) {
            composable(Screen.Login.route) {
                LoginScreen(onLoginSuccess = {
                    navController.navigate(Screen.Research.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                })
            }
            composable(Screen.Research.route) {
                HomeScreen(
                    viewModel = homeVm,
                    paddingValues = paddingValues,
                    darkTheme = darkTheme,
                    onToggleDark = onToggleDark,
                    onArticleClick = { article ->
                        selectedArticle = article
                        navController.navigate("article_detail")
                    },
                    onAskMaverick = { query ->
                        navController.navigate(Screen.Chat.route)
                    }
                )
            }
            composable(Screen.Chat.route) {
                ChatScreen(viewModel = chatVm, paddingValues = paddingValues)
            }
            composable(Screen.Trends.route) {
                TrendsScreen(paddingValues = paddingValues)
            }
            composable("article_detail") {
                selectedArticle?.let { article ->
                    ArticleDetailScreen(
                        article = article,
                        onBack = { navController.popBackStack() },
                        onAskMaverick = {
                            navController.navigate(Screen.Chat.route)
                        }
                    )
                }
            }
        }
    }
}
