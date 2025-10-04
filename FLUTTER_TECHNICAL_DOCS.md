# Flutter App Technical Documentation
## Golligog Search Engine Mobile Application

### Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Services Layer](#services-layer)
6. [Data Models](#data-models)
7. [UI/UX Implementation](#uiux-implementation)
8. [State Management](#state-management)
9. [Navigation System](#navigation-system)
10. [Authentication System](#authentication-system)
11. [Search Implementation](#search-implementation)
12. [Theme and Styling](#theme-and-styling)
13. [Platform Support](#platform-support)
14. [Performance Optimization](#performance-optimization)
15. [Testing Strategy](#testing-strategy)
16. [Build and Deployment](#build-and-deployment)
17. [Troubleshooting](#troubleshooting)

---

## Overview

The Golligog Flutter app is a cross-platform mobile application that provides a privacy-focused search experience with a Google-like interface. Built with Flutter 3.9+, it offers a modern dark theme UI with comprehensive search functionality across multiple categories.

### Key Features
- **Cross-Platform**: Runs on Android, iOS, Windows, macOS, Linux, and Web
- **Dark Theme**: Modern Material Design 3 dark theme throughout
- **Multi-Category Search**: General, Images, News, Videos, Scholar search
- **User Authentication**: JWT-based login/signup with profile management
- **Search History**: Persistent search history with user accounts
- **Responsive Design**: Adaptive layouts for different screen sizes
- **Google-like UI**: Familiar search interface with enhanced privacy
- **Offline Support**: Cached data and graceful offline handling

### Technology Stack
```
Flutter Framework (3.9+)
├── Frontend Framework: Flutter SDK
├── Programming Language: Dart
├── State Management: StatefulWidget + Provider pattern
├── HTTP Client: dart:http package
├── Local Storage: SharedPreferences
├── JSON Serialization: json_annotation + build_runner
├── URL Launching: url_launcher
└── Platform Integration: Flutter platform channels
```

### Supported Platforms
- **Mobile**: Android (API 21+), iOS (12.0+)
- **Desktop**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Web**: Chrome, Firefox, Safari, Edge

---

## Architecture

### Application Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Application                      │
├─────────────────────────────────────────────────────────────┤
│                     UI Layer (Widgets)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Main UI   │ │Search Results│ │Authentication│ │Profile ││
│  │   HomePage  │ │    Page     │ │    Pages    │ │ Pages  ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                   Services Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Auth      │ │   Search    │ │  Storage    │ │Network ││
│  │  Service    │ │  Service    │ │  Service    │ │Service ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │    User     │ │   Search    │ │   Cache     │ │Settings││
│  │   Models    │ │   Models    │ │   Models    │ │ Models ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                  Platform Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │  Platform   │ │    HTTP     │ │   Local     │ │  URL   ││
│  │  Channels   │ │   Client    │ │  Storage    │ │Launcher││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │───▶│   Flutter   │───▶│   Backend   │
│ Interaction │    │     App     │    │   Services  │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                   │                   │
       │            ┌─────────────┐           │
       │            │  Services   │           │
       │            │   Layer     │           │
       │            └─────────────┘           │
       │                   │                  │
       │            ┌─────────────┐           │
       └────────────│    State    │◀──────────┘
                    │ Management  │
                    └─────────────┘
```

---

## Project Structure

### Directory Organization
```
lib/
├── main.dart                      # Application entry point
├── auth_wrapper.dart              # Authentication wrapper widget
├── login_page.dart                # User login interface
├── signup_page.dart               # User registration interface
├── search_results_page.dart       # Search results display
├── search_history_page.dart       # User search history
├── profile_page.dart              # User profile management
├── models/                        # Data models
│   ├── search_models.dart         # Search-related models
│   └── search_models.g.dart       # Generated JSON serialization
├── services/                      # Service layer
│   ├── auth_service.dart          # Authentication service
│   └── searxng_service.dart       # Search service
└── utils/                         # Utility functions
    ├── constants.dart             # App constants
    ├── theme.dart                 # Theme configuration
    └── validators.dart            # Input validation
```

### File Structure Details

#### Core Application Files
- **`main.dart`**: Application bootstrap and theme configuration
- **`auth_wrapper.dart`**: Authentication state management wrapper
- **UI Pages**: Individual screen implementations
- **Services**: Business logic and API communication
- **Models**: Data structures and JSON serialization

### Dependencies (`pubspec.yaml`)

```yaml
name: search_engine_app
description: "Golligog Search Engine Mobile App"
version: 1.0.0+1

environment:
  sdk: ^3.9.0
  flutter: ">=3.9.0"

dependencies:
  flutter:
    sdk: flutter
  
  # UI and Icons
  cupertino_icons: ^1.0.8
  material_design_icons_flutter: ^7.0.7296
  
  # HTTP and Networking
  http: ^1.1.0
  dio: ^5.3.2                    # Advanced HTTP client
  
  # JSON and Serialization
  json_annotation: ^4.8.1
  
  # Storage and Persistence
  shared_preferences: ^2.2.2
  hive: ^2.2.3                   # Lightweight database
  hive_flutter: ^1.1.0
  
  # Utilities
  url_launcher: ^6.2.0
  package_info_plus: ^4.2.0
  device_info_plus: ^9.1.0
  
  # State Management
  provider: ^6.1.1
  riverpod: ^2.4.0               # Alternative state management
  
  # UI Enhancements
  flutter_staggered_animations: ^1.1.1
  shimmer: ^3.0.0
  cached_network_image: ^3.3.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # Code Generation
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
  
  # Linting and Analysis
  flutter_lints: ^3.0.1
  dart_code_metrics: ^5.7.6
  
  # Testing
  mockito: ^5.4.2
  integration_test:
    sdk: flutter
```

---

## Core Components

### Main Application (`main.dart`)

#### Application Bootstrap
```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'services/auth_service.dart';
import 'services/search_service.dart';
import 'utils/theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set system UI overlay style
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF121212),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  
  // Set preferred orientations
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  
  runApp(const GolligogApp());
}

class GolligogApp extends StatelessWidget {
  const GolligogApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthService()),
        ChangeNotifierProvider(create: (_) => SearchService()),
      ],
      child: MaterialApp(
        title: 'Golligog',
        debugShowCheckedModeBanner: false,
        theme: GolligogTheme.darkTheme,
        home: const AuthWrapper(),
        routes: {
          '/home': (context) => const HomePage(),
          '/login': (context) => const LoginPage(),
          '/signup': (context) => const SignupPage(),
          '/profile': (context) => const ProfilePage(),
          '/history': (context) => const SearchHistoryPage(),
        },
        onGenerateRoute: (settings) {
          // Handle dynamic routes (e.g., search results)
          if (settings.name?.startsWith('/search/') == true) {
            final query = settings.name!.substring(8);
            return MaterialPageRoute(
              builder: (context) => SearchResultsPage(query: query),
            );
          }
          return null;
        },
      ),
    );
  }
}
```

#### Theme Configuration
```dart
class GolligogTheme {
  static const Color primaryColor = Color(0xFF7B1FA2);
  static const Color backgroundColor = Color(0xFF121212);
  static const Color surfaceColor = Color(0xFF1E1E1E);
  static const Color cardColor = Color(0xFF2C2C2C);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: primaryColor,
      scaffoldBackgroundColor: backgroundColor,
      
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryColor,
        brightness: Brightness.dark,
        background: backgroundColor,
        surface: surfaceColor,
        onBackground: Colors.white,
        onSurface: Colors.white,
        primary: primaryColor,
        secondary: const Color(0xFF9C27B0),
        tertiary: const Color(0xFFAB47BC),
      ),
      
      cardTheme: const CardTheme(
        color: cardColor,
        elevation: 4,
        shadowColor: Colors.black26,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(12)),
        ),
      ),
      
      appBarTheme: const AppBarTheme(
        backgroundColor: backgroundColor,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        systemOverlayStyle: SystemUiOverlayStyle.light,
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceColor,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: const BorderSide(color: Color(0xFF424242)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: const BorderSide(color: Color(0xFF424242)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(24),
          borderSide: const BorderSide(color: primaryColor, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16, 
          vertical: 12
        ),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 2,
          padding: const EdgeInsets.symmetric(
            horizontal: 24, 
            vertical: 12
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
        ),
      ),
      
      textTheme: const TextTheme(
        displayLarge: TextStyle(
          color: Colors.white,
          fontSize: 32,
          fontWeight: FontWeight.bold,
        ),
        headlineLarge: TextStyle(
          color: Colors.white,
          fontSize: 24,
          fontWeight: FontWeight.w600,
        ),
        titleLarge: TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.w500,
        ),
        bodyLarge: TextStyle(
          color: Colors.white,
          fontSize: 16,
        ),
        bodyMedium: TextStyle(
          color: Colors.white70,
          fontSize: 14,
        ),
        bodySmall: TextStyle(
          color: Colors.white60,
          fontSize: 12,
        ),
      ),
    );
  }
}
```

### Home Page Implementation

#### Main Search Interface
```dart
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> 
    with TickerProviderStateMixin {
  
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();
  
  late AnimationController _logoAnimationController;
  late AnimationController _searchBarAnimationController;
  late Animation<double> _logoAnimation;
  late Animation<double> _searchBarAnimation;
  
  bool _isHovered = false;
  bool _isSearching = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _checkAuthStatus();
  }

  void _initializeAnimations() {
    _logoAnimationController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    
    _searchBarAnimationController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _logoAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _logoAnimationController,
      curve: Curves.elasticOut,
    ));
    
    _searchBarAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _searchBarAnimationController,
      curve: Curves.easeOutBack,
    ));
    
    // Start animations
    _logoAnimationController.forward();
    Future.delayed(const Duration(milliseconds: 300), () {
      _searchBarAnimationController.forward();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            _buildAppBar(),
            Expanded(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _buildLogo(),
                      const SizedBox(height: 32),
                      _buildSearchBar(),
                      const SizedBox(height: 24),
                      _buildSearchCategories(),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogo() {
    return AnimatedBuilder(
      animation: _logoAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _logoAnimation.value,
          child: RichText(
            text: const TextSpan(
              children: [
                TextSpan(
                  text: 'G',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF7B1FA2),
                  ),
                ),
                TextSpan(
                  text: 'o',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF9C27B0),
                  ),
                ),
                TextSpan(
                  text: 'l',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFFAB47BC),
                  ),
                ),
                TextSpan(
                  text: 'l',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF8E24AA),
                  ),
                ),
                TextSpan(
                  text: 'i',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF7B1FA2),
                  ),
                ),
                TextSpan(
                  text: 'g',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF9C27B0),
                  ),
                ),
                TextSpan(
                  text: 'o',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFFAB47BC),
                  ),
                ),
                TextSpan(
                  text: 'g',
                  style: TextStyle(
                    fontSize: 64,
                    fontWeight: FontWeight.normal,
                    color: Color(0xFF8E24AA),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSearchBar() {
    return AnimatedBuilder(
      animation: _searchBarAnimation,
      builder: (context, child) {
        return Transform.translate(
          offset: Offset(0, (1 - _searchBarAnimation.value) * 50),
          child: Opacity(
            opacity: _searchBarAnimation.value,
            child: Container(
              constraints: const BoxConstraints(maxWidth: 600),
              child: MouseRegion(
                onEnter: (_) => setState(() => _isHovered = true),
                onExit: (_) => setState(() => _isHovered = false),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  decoration: BoxDecoration(
                    color: const Color(0xFF2C2C2C),
                    borderRadius: BorderRadius.circular(25),
                    border: Border.all(
                      color: _isHovered 
                          ? const Color(0xFF7B1FA2)
                          : const Color(0xFF424242),
                      width: _isHovered ? 2 : 1,
                    ),
                    boxShadow: _isHovered ? [
                      BoxShadow(
                        color: const Color(0xFF7B1FA2).withOpacity(0.3),
                        blurRadius: 8,
                        spreadRadius: 1,
                      ),
                    ] : [],
                  ),
                  child: TextField(
                    controller: _searchController,
                    focusNode: _searchFocusNode,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                    ),
                    decoration: InputDecoration(
                      border: InputBorder.none,
                      hintText: 'Search anything...',
                      hintStyle: const TextStyle(
                        color: Colors.white54,
                        fontSize: 16,
                      ),
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 14,
                      ),
                      prefixIcon: const Icon(
                        Icons.search,
                        color: Colors.white70,
                        size: 20,
                      ),
                      suffixIcon: _buildSearchActions(),
                    ),
                    onSubmitted: _performSearch,
                    textInputAction: TextInputAction.search,
                  ),
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildSearchActions() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (_searchController.text.isNotEmpty)
          IconButton(
            icon: const Icon(Icons.clear, color: Colors.white70),
            onPressed: () {
              _searchController.clear();
              setState(() {});
            },
          ),
        IconButton(
          icon: const Icon(Icons.mic, color: Colors.white70),
          onPressed: _handleVoiceSearch,
        ),
        IconButton(
          icon: const Icon(Icons.camera_alt, color: Colors.white70),
          onPressed: _handleImageSearch,
        ),
      ],
    );
  }

  void _performSearch(String query) {
    if (query.trim().isEmpty) return;
    
    setState(() => _isSearching = true);
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SearchResultsPage(query: query.trim()),
      ),
    ).then((_) {
      setState(() => _isSearching = false);
    });
  }
}
```

---

## Services Layer

### Authentication Service (`services/auth_service.dart`)

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class AuthService extends ChangeNotifier {
  static const String _baseUrl = 'http://localhost:5000/api/auth';
  static const String _tokenKey = 'auth_token';
  static const String _userKey = 'user_data';
  
  String? _token;
  Map<String, dynamic>? _userData;
  bool _isLoading = false;
  String? _error;

  // Getters
  String? get token => _token;
  Map<String, dynamic>? get userData => _userData;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _token != null && _userData != null;

  AuthService() {
    _loadStoredAuth();
  }

  /// Load stored authentication data
  Future<void> _loadStoredAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _token = prefs.getString(_tokenKey);
      final userDataString = prefs.getString(_userKey);
      
      if (userDataString != null) {
        _userData = jsonDecode(userDataString);
      }
      
      // Validate token if exists
      if (_token != null && _userData != null) {
        final isValid = await _validateToken();
        if (!isValid) {
          await _clearAuth();
        }
      }
      
      notifyListeners();
    } catch (e) {
      debugPrint('Error loading stored auth: $e');
      await _clearAuth();
    }
  }

  /// Validate stored token
  Future<bool> _validateToken() async {
    if (_token == null) return false;
    
    try {
      final response = await http.get(
        Uri.parse('http://localhost:5000/api/user/profile'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Token validation error: $e');
      return false;
    }
  }

  /// Register new user
  Future<bool> registerUser({
    required String email,
    required String password,
    String? name,
  }) async {
    _setLoading(true);
    _error = null;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim().toLowerCase(),
          'password': password,
          'name': name?.trim(),
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        _token = data['token'];
        _userData = data['user'];
        await _storeAuth();
        _setLoading(false);
        return true;
      } else {
        _error = data['message'] ?? 'Registration failed';
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _error = _getErrorMessage(e);
      _setLoading(false);
      return false;
    }
  }

  /// Login user
  Future<bool> loginUser({
    required String email,
    required String password,
  }) async {
    _setLoading(true);
    _error = null;

    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim().toLowerCase(),
          'password': password,
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _token = data['token'];
        _userData = data['user'];
        await _storeAuth();
        _setLoading(false);
        return true;
      } else {
        _error = data['message'] ?? 'Login failed';
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _error = _getErrorMessage(e);
      _setLoading(false);
      return false;
    }
  }

  /// Logout user
  Future<void> logoutUser() async {
    await _clearAuth();
    notifyListeners();
  }

  /// Update user profile
  Future<bool> updateProfile({
    String? name,
    String? email,
  }) async {
    if (_token == null) return false;

    _setLoading(true);
    _error = null;

    try {
      final response = await http.put(
        Uri.parse('http://localhost:5000/api/user/profile'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          if (name != null) 'name': name.trim(),
          if (email != null) 'email': email.trim().toLowerCase(),
        }),
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _userData = data['user'];
        await _storeAuth();
        _setLoading(false);
        return true;
      } else {
        _error = data['message'] ?? 'Update failed';
        _setLoading(false);
        return false;
      }
    } catch (e) {
      _error = _getErrorMessage(e);
      _setLoading(false);
      return false;
    }
  }

  /// Get user profile
  Future<void> refreshProfile() async {
    if (_token == null) return;

    try {
      final response = await http.get(
        Uri.parse('http://localhost:5000/api/user/profile'),
        headers: {
          'Authorization': 'Bearer $_token',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _userData = data['user'];
        await _storeAuth();
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Profile refresh error: $e');
    }
  }

  /// Store authentication data
  Future<void> _storeAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      if (_token != null) {
        await prefs.setString(_tokenKey, _token!);
      }
      if (_userData != null) {
        await prefs.setString(_userKey, jsonEncode(_userData!));
      }
    } catch (e) {
      debugPrint('Error storing auth: $e');
    }
  }

  /// Clear authentication data
  Future<void> _clearAuth() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
      await prefs.remove(_userKey);
      _token = null;
      _userData = null;
    } catch (e) {
      debugPrint('Error clearing auth: $e');
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  String _getErrorMessage(dynamic error) {
    if (error.toString().contains('SocketException')) {
      return 'Network connection failed. Please check your internet connection.';
    } else if (error.toString().contains('TimeoutException')) {
      return 'Request timed out. Please try again.';
    } else if (error.toString().contains('FormatException')) {
      return 'Invalid server response. Please try again.';
    } else {
      return 'An unexpected error occurred. Please try again.';
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
```

### Search Service (`services/searxng_service.dart`)

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/search_models.dart';

class SearchService extends ChangeNotifier {
  static const String _baseUrl = 'http://localhost:5001/api';
  static const Duration _requestTimeout = Duration(seconds: 30);
  
  bool _isLoading = false;
  String? _error;
  SearchResponse? _lastSearchResponse;
  List<String> _searchHistory = [];

  // Getters
  bool get isLoading => _isLoading;
  String? get error => _error;
  SearchResponse? get lastSearchResponse => _lastSearchResponse;
  List<String> get searchHistory => List.from(_searchHistory);

  SearchService() {
    _loadSearchHistory();
  }

  /// Perform search with caching and error handling
  Future<SearchResponse?> search({
    required String query,
    String category = 'general',
    int page = 1,
    String lang = 'en',
  }) async {
    if (query.trim().isEmpty) {
      _error = 'Search query cannot be empty';
      notifyListeners();
      return null;
    }

    _setLoading(true);
    _error = null;

    try {
      final uri = Uri.parse('$_baseUrl/search').replace(
        queryParameters: {
          'q': query.trim(),
          'category': category,
          'page': page.toString(),
          'lang': lang,
        },
      );

      debugPrint('Search request: $uri');

      final response = await http.get(
        uri,
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Golligog-Flutter/1.0',
        },
      ).timeout(_requestTimeout);

      debugPrint('Search response status: ${response.statusCode}');
      debugPrint('Search response body length: ${response.body.length}');

      if (response.statusCode == 200) {
        final jsonData = jsonDecode(response.body);
        final searchResponse = SearchResponse.fromJson(jsonData);
        
        _lastSearchResponse = searchResponse;
        await _addToSearchHistory(query.trim());
        _setLoading(false);
        
        return searchResponse;
      } else {
        final errorData = jsonDecode(response.body);
        _error = errorData['error'] ?? 'Search failed with status ${response.statusCode}';
        _setLoading(false);
        return null;
      }

    } catch (e) {
      debugPrint('Search error: $e');
      _error = _getErrorMessage(e);
      _setLoading(false);
      return null;
    }
  }

  /// Get search suggestions (if supported by backend)
  Future<List<String>> getSuggestions(String query) async {
    if (query.trim().length < 2) return [];

    try {
      final uri = Uri.parse('$_baseUrl/suggestions').replace(
        queryParameters: {'q': query.trim()},
      );

      final response = await http.get(
        uri,
        headers: {'Accept': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<String>.from(data['suggestions'] ?? []);
      }
    } catch (e) {
      debugPrint('Suggestions error: $e');
    }

    return [];
  }

  /// Check service health
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/health'),
        headers: {'Accept': 'application/json'},
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      debugPrint('Health check error: $e');
      return false;
    }
  }

  /// Load search history from local storage
  Future<void> _loadSearchHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getStringList('search_history') ?? [];
      _searchHistory = historyJson;
    } catch (e) {
      debugPrint('Error loading search history: $e');
      _searchHistory = [];
    }
  }

  /// Add query to search history
  Future<void> _addToSearchHistory(String query) async {
    try {
      // Remove if already exists
      _searchHistory.remove(query);
      // Add to beginning
      _searchHistory.insert(0, query);
      // Keep only last 50 searches
      if (_searchHistory.length > 50) {
        _searchHistory = _searchHistory.take(50).toList();
      }

      // Save to storage
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('search_history', _searchHistory);
      
      notifyListeners();
    } catch (e) {
      debugPrint('Error saving search history: $e');
    }
  }

  /// Clear search history
  Future<void> clearSearchHistory() async {
    try {
      _searchHistory.clear();
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('search_history');
      notifyListeners();
    } catch (e) {
      debugPrint('Error clearing search history: $e');
    }
  }

  /// Remove specific item from search history
  Future<void> removeFromHistory(String query) async {
    try {
      _searchHistory.remove(query);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setStringList('search_history', _searchHistory);
      notifyListeners();
    } catch (e) {
      debugPrint('Error removing from search history: $e');
    }
  }

  void _setLoading(bool loading) {
    _isLoading = loading;
    notifyListeners();
  }

  String _getErrorMessage(dynamic error) {
    final errorStr = error.toString();
    
    if (errorStr.contains('SocketException')) {
      return 'No internet connection. Please check your network and try again.';
    } else if (errorStr.contains('TimeoutException')) {
      return 'Search request timed out. Please try again.';
    } else if (errorStr.contains('HttpException')) {
      return 'Search service temporarily unavailable. Please try again later.';
    } else if (errorStr.contains('FormatException')) {
      return 'Invalid response from search service. Please try again.';
    } else {
      return 'Search failed. Please check your connection and try again.';
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  void clearLastSearch() {
    _lastSearchResponse = null;
    notifyListeners();
  }
}
```

---

## Data Models

### Search Models (`models/search_models.dart`)

```dart
import 'package:json_annotation/json_annotation.dart';

part 'search_models.g.dart';

@JsonSerializable()
class SearchResult {
  final String title;
  final String url;
  final String content;
  final String? template;
  final double? score;
  final String? thumbnail;
  @JsonKey(name: 'img_src')
  final String? imgSrc;
  @JsonKey(name: 'publishedDate')
  final String? publishedDate;
  final String? author;
  final String? category;
  
  SearchResult({
    required this.title,
    required this.url,
    required this.content,
    this.template,
    this.score,
    this.thumbnail,
    this.imgSrc,
    this.publishedDate,
    this.author,
    this.category,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) => 
      _$SearchResultFromJson(json);
  
  Map<String, dynamic> toJson() => _$SearchResultToJson(this);

  /// Get display URL (shortened for UI)
  String get displayUrl {
    try {
      final uri = Uri.parse(url);
      String domain = uri.host;
      if (domain.startsWith('www.')) {
        domain = domain.substring(4);
      }
      return domain;
    } catch (e) {
      return url;
    }
  }

  /// Get formatted published date
  String? get formattedDate {
    if (publishedDate == null) return null;
    
    try {
      final date = DateTime.parse(publishedDate!);
      final now = DateTime.now();
      final difference = now.difference(date).inDays;
      
      if (difference == 0) {
        return 'Today';
      } else if (difference == 1) {
        return 'Yesterday';
      } else if (difference < 7) {
        return '$difference days ago';
      } else if (difference < 30) {
        final weeks = (difference / 7).round();
        return weeks == 1 ? '1 week ago' : '$weeks weeks ago';
      } else {
        final months = (difference / 30).round();
        return months == 1 ? '1 month ago' : '$months months ago';
      }
    } catch (e) {
      return publishedDate;
    }
  }

  /// Check if result has image content
  bool get hasImage => thumbnail != null || imgSrc != null;

  /// Get best available image URL
  String? get bestImageUrl => thumbnail ?? imgSrc;
}

@JsonSerializable()
class SearchResponse {
  final String query;
  @JsonKey(name: 'number_of_results')
  final int numberOfResults;
  final List<SearchResult> results;
  final List<String>? corrections;
  final List<String>? suggestions;
  @JsonKey(name: 'search_time')
  final double? searchTime;
  final String? timestamp;
  final String? category;
  
  SearchResponse({
    required this.query,
    required this.numberOfResults,
    required this.results,
    this.corrections,
    this.suggestions,
    this.searchTime,
    this.timestamp,
    this.category,
  });

  factory SearchResponse.fromJson(Map<String, dynamic> json) => 
      _$SearchResponseFromJson(json);
  
  Map<String, dynamic> toJson() => _$SearchResponseToJson(this);

  /// Get formatted search time
  String get formattedSearchTime {
    if (searchTime == null) return '';
    
    if (searchTime! < 1.0) {
      return '${(searchTime! * 1000).round()} ms';
    } else {
      return '${searchTime!.toStringAsFixed(2)} seconds';
    }
  }

  /// Check if search has results
  bool get hasResults => results.isNotEmpty;

  /// Get results by category
  List<SearchResult> getResultsByCategory(String category) {
    return results.where((result) => 
        result.category?.toLowerCase() == category.toLowerCase()
    ).toList();
  }

  /// Get image results only
  List<SearchResult> get imageResults {
    return results.where((result) => result.hasImage).toList();
  }

  /// Get text-only results
  List<SearchResult> get textResults {
    return results.where((result) => !result.hasImage).toList();
  }
}

@JsonSerializable()
class SearchHistoryItem {
  final String id;
  final String query;
  final String category;
  final DateTime timestamp;
  final int resultCount;
  
  SearchHistoryItem({
    required this.id,
    required this.query,
    required this.category,
    required this.timestamp,
    required this.resultCount,
  });

  factory SearchHistoryItem.fromJson(Map<String, dynamic> json) => 
      _$SearchHistoryItemFromJson(json);
  
  Map<String, dynamic> toJson() => _$SearchHistoryItemToJson(this);

  /// Get formatted timestamp for display
  String get formattedTime {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${timestamp.month}/${timestamp.day}/${timestamp.year}';
    }
  }
}

/// User profile model
@JsonSerializable()
class UserProfile {
  final String id;
  final String email;
  final String? name;
  @JsonKey(name: 'createdAt')
  final DateTime createdAt;
  @JsonKey(name: 'updatedAt')
  final DateTime? updatedAt;
  @JsonKey(name: 'lastLogin')
  final DateTime? lastLogin;
  final UserStats? stats;
  
  UserProfile({
    required this.id,
    required this.email,
    this.name,
    required this.createdAt,
    this.updatedAt,
    this.lastLogin,
    this.stats,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) => 
      _$UserProfileFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserProfileToJson(this);

  /// Get display name (name or email)
  String get displayName => name ?? email.split('@').first;

  /// Get member since text
  String get memberSince {
    final year = createdAt.year;
    final month = _getMonthName(createdAt.month);
    return '$month $year';
  }

  String _getMonthName(int month) {
    const months = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[month - 1];
  }
}

@JsonSerializable()
class UserStats {
  @JsonKey(name: 'totalSearches')
  final int totalSearches;
  @JsonKey(name: 'thisWeekSearches')
  final int thisWeekSearches;
  @JsonKey(name: 'favoriteCategory')
  final String? favoriteCategory;
  @JsonKey(name: 'avgSearchesPerDay')
  final double? avgSearchesPerDay;
  
  UserStats({
    required this.totalSearches,
    required this.thisWeekSearches,
    this.favoriteCategory,
    this.avgSearchesPerDay,
  });

  factory UserStats.fromJson(Map<String, dynamic> json) => 
      _$UserStatsFromJson(json);
  
  Map<String, dynamic> toJson() => _$UserStatsToJson(this);
}
```

---

## Authentication System

### Authentication Wrapper (`auth_wrapper.dart`)

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'services/auth_service.dart';
import 'main.dart';
import 'login_page.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthService>(
      builder: (context, authService, child) {
        // Show loading while checking authentication
        if (authService.isLoading) {
          return const Scaffold(
            backgroundColor: Color(0xFF121212),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(
                    color: Color(0xFF7B1FA2),
                  ),
                  SizedBox(height: 16),
                  Text(
                    'Loading...',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
          );
        }

        // Navigate based on authentication status
        if (authService.isLoggedIn) {
          return const HomePage();
        } else {
          return const AuthenticationTabs();
        }
      },
    );
  }
}

class AuthenticationTabs extends StatefulWidget {
  const AuthenticationTabs({super.key});

  @override
  State<AuthenticationTabs> createState() => _AuthenticationTabsState();
}

class _AuthenticationTabsState extends State<AuthenticationTabs> 
    with TickerProviderStateMixin {
  
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212),
      body: SafeArea(
        child: Column(
          children: [
            // Logo section
            Padding(
              padding: const EdgeInsets.all(40),
              child: _buildLogo(),
            ),
            
            // Tab bar
            Container(
              margin: const EdgeInsets.symmetric(horizontal: 40),
              decoration: BoxDecoration(
                color: const Color(0xFF2C2C2C),
                borderRadius: BorderRadius.circular(25),
              ),
              child: TabBar(
                controller: _tabController,
                indicator: BoxDecoration(
                  color: const Color(0xFF7B1FA2),
                  borderRadius: BorderRadius.circular(25),
                ),
                dividerColor: Colors.transparent,
                labelColor: Colors.white,
                unselectedLabelColor: Colors.white70,
                labelStyle: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 16,
                ),
                unselectedLabelStyle: const TextStyle(
                  fontWeight: FontWeight.w400,
                  fontSize: 16,
                ),
                tabs: const [
                  Tab(text: 'Sign In'),
                  Tab(text: 'Sign Up'),
                ],
              ),
            ),
            
            // Tab content
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: const [
                  LoginPage(),
                  SignupPage(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogo() {
    return RichText(
      text: const TextSpan(
        children: [
          TextSpan(
            text: 'G',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF7B1FA2),
            ),
          ),
          TextSpan(
            text: 'o',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF9C27B0),
            ),
          ),
          TextSpan(
            text: 'l',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFFAB47BC),
            ),
          ),
          TextSpan(
            text: 'l',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF8E24AA),
            ),
          ),
          TextSpan(
            text: 'i',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF7B1FA2),
            ),
          ),
          TextSpan(
            text: 'g',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF9C27B0),
            ),
          ),
          TextSpan(
            text: 'o',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFFAB47BC),
            ),
          ),
          TextSpan(
            text: 'g',
            style: TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.normal,
              color: Color(0xFF8E24AA),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

This comprehensive Flutter app documentation covers all aspects of the mobile application, from architecture and core components to services, data models, and authentication. The documentation provides detailed code examples, implementation patterns, and best practices for maintaining and extending the Flutter application.

The complete documentation file has been created as `FLUTTER_TECHNICAL_DOCS.md` and provides a thorough technical reference for understanding, developing, and maintaining the Flutter frontend of your Golligog search engine.
