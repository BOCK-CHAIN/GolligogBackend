# Flutter Frontend Development Guide

## Overview

The Golligog Flutter application is a cross-platform mobile and web app that provides a privacy-focused search experience with a modern dark theme interface. This guide covers the complete Flutter development workflow, architecture, and implementation details.

## Technology Stack

```
Flutter Framework (3.13+)
├── Programming Language: Dart
├── UI Framework: Material Design 3
├── State Management: StatefulWidget + Provider pattern
├── HTTP Client: dart:http package
├── Local Storage: SharedPreferences
├── JSON Serialization: json_annotation + build_runner
├── URL Launching: url_launcher
└── Platform Integration: Flutter platform channels
```

## Project Structure

```
flutter/search_engine_app/
├── lib/
│   ├── main.dart                      # Application entry point
│   ├── auth_wrapper.dart              # Authentication wrapper
│   ├── login_page.dart                # User login interface
│   ├── signup_page.dart               # User registration interface
│   ├── search_results_page.dart       # Search results display
│   ├── search_history_page.dart       # User search history
│   ├── profile_page.dart              # User profile management
│   ├── models/
│   │   ├── search_models.dart         # Search-related models
│   │   └── search_models.g.dart       # Generated JSON serialization
│   ├── services/
│   │   ├── auth_service.dart          # Authentication service
│   │   └── searxng_service.dart       # Search service
│   ├── config/
│   │   └── app_config.dart            # Environment configuration
│   └── utils/
│       ├── constants.dart             # App constants
│       ├── theme.dart                 # Theme configuration
│       └── validators.dart            # Input validation
├── android/                           # Android-specific files
├── ios/                               # iOS-specific files
├── web/                               # Web-specific files
├── windows/                           # Windows-specific files
├── linux/                             # Linux-specific files
├── macos/                             # macOS-specific files
└── pubspec.yaml                       # Dependencies and configuration
```

## Dependencies Configuration

### pubspec.yaml
```yaml
name: search_engine_app
description: "Golligog Search Engine Mobile App"
version: 1.0.0+1

environment:
  sdk: ^3.9.0
  flutter: ">=3.13.0"

dependencies:
  flutter:
    sdk: flutter
  
  # UI and Icons
  cupertino_icons: ^1.0.8
  material_design_icons_flutter: ^7.0.7296
  
  # HTTP and Networking
  http: ^1.1.0
  dio: ^5.3.2
  
  # JSON and Serialization
  json_annotation: ^4.8.1
  
  # Storage and Persistence
  shared_preferences: ^2.2.2
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  
  # Utilities
  url_launcher: ^6.2.0
  package_info_plus: ^4.2.0
  device_info_plus: ^9.1.0
  
  # State Management
  provider: ^6.1.1
  
  # UI Enhancements
  flutter_staggered_animations: ^1.1.1
  shimmer: ^3.0.0
  cached_network_image: ^3.3.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.7
  json_serializable: ^6.7.1
  flutter_lints: ^3.0.1

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
```

## Core Components

### 1. Main Application Entry Point

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'services/auth_service.dart';
import 'services/search_service.dart';
import 'utils/theme.dart';
import 'auth_wrapper.dart';

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
      ),
    );
  }
}
```

### 2. Theme Configuration

```dart
// lib/utils/theme.dart
import 'package:flutter/material.dart';

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
      ),
    );
  }
}
```

### 3. Search Service Implementation

```dart
// lib/services/searxng_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/search_models.dart';

class SearchService extends ChangeNotifier {
  static const String baseUrl = 'http://localhost:5001';
  
  List<SearchResult> _searchResults = [];
  bool _isLoading = false;
  String? _error;
  
  List<SearchResult> get searchResults => _searchResults;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<List<SearchResult>> search({
    required String query,
    String category = 'general',
    int page = 1,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final uri = Uri.parse('$baseUrl/search').replace(queryParameters: {
        'q': query,
        'category': category,
        'page': page.toString(),
        'format': 'json',
      });

      final response = await http.get(
        uri,
        headers: {'Content-Type': 'application/json'},
      ).timeout(AppConfig.apiTimeout);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final results = (data['results'] as List)
            .map((result) => SearchResult.fromJson(result))
            .toList();

        _searchResults = results;
        _isLoading = false;
        notifyListeners();
        
        return results;
      } else {
        throw Exception('Search failed: ${response.statusCode}');
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      rethrow;
    }
  }

  Future<List<SearchResult>> searchImages(String query) async {
    return search(query: query, category: 'images');
  }

  Future<List<SearchResult>> searchNews(String query) async {
    return search(query: query, category: 'news');
  }

  Future<List<SearchResult>> searchVideos(String query) async {
    return search(query: query, category: 'videos');
  }

  void clearResults() {
    _searchResults.clear();
    _error = null;
    notifyListeners();
  }
}
```

### 4. Data Models

```dart
// lib/models/search_models.dart
import 'package:json_annotation/json_annotation.dart';

part 'search_models.g.dart';

@JsonSerializable()
class SearchResult {
  final String title;
  final String url;
  final String content;
  final String? thumbnail;
  final String? publishedDate;
  final String category;

  SearchResult({
    required this.title,
    required this.url,
    required this.content,
    this.thumbnail,
    this.publishedDate,
    required this.category,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) =>
      _$SearchResultFromJson(json);

  Map<String, dynamic> toJson() => _$SearchResultToJson(this);
}

@JsonSerializable()
class SearchResponse {
  final List<SearchResult> results;
  final int totalResults;
  final int currentPage;
  final int totalPages;
  final String query;

  SearchResponse({
    required this.results,
    required this.totalResults,
    required this.currentPage,
    required this.totalPages,
    required this.query,
  });

  factory SearchResponse.fromJson(Map<String, dynamic> json) =>
      _$SearchResponseFromJson(json);

  Map<String, dynamic> toJson() => _$SearchResponseToJson(this);
}
```

## UI Implementation

### 1. Home Page with Search Interface

```dart
// lib/home_page.dart (excerpt)
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _searchController = TextEditingController();
  final FocusNode _searchFocusNode = FocusNode();

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

  Widget _buildSearchBar() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 600),
      child: TextField(
        controller: _searchController,
        focusNode: _searchFocusNode,
        style: const TextStyle(color: Colors.white, fontSize: 16),
        decoration: InputDecoration(
          border: InputBorder.none,
          hintText: 'Search anything...',
          hintStyle: const TextStyle(color: Colors.white54, fontSize: 16),
          contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          prefixIcon: const Icon(Icons.search, color: Colors.white70, size: 20),
        ),
        onSubmitted: _performSearch,
        textInputAction: TextInputAction.search,
      ),
    );
  }

  void _performSearch(String query) {
    if (query.trim().isEmpty) return;
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SearchResultsPage(query: query.trim()),
      ),
    );
  }
}
```

### 2. Search Results Page

```dart
// lib/search_results_page.dart
class SearchResultsPage extends StatefulWidget {
  final String query;
  
  const SearchResultsPage({super.key, required this.query});

  @override
  State<SearchResultsPage> createState() => _SearchResultsPageState();
}

class _SearchResultsPageState extends State<SearchResultsPage> {
  late SearchService _searchService;
  String _currentCategory = 'general';
  final List<String> _categories = ['general', 'images', 'news', 'videos'];

  @override
  void initState() {
    super.initState();
    _searchService = Provider.of<SearchService>(context, listen: false);
    _performSearch();
  }

  void _performSearch() {
    _searchService.search(
      query: widget.query,
      category: _currentCategory,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Search: ${widget.query}'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: _buildCategoryTabs(),
        ),
      ),
      body: Consumer<SearchService>(
        builder: (context, searchService, child) {
          if (searchService.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (searchService.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.error_outline, size: 64, color: Colors.red[400]),
                  const SizedBox(height: 16),
                  Text(
                    'Search failed',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    searchService.error!,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _performSearch,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (searchService.searchResults.isEmpty) {
            return const Center(
              child: Text('No results found'),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: searchService.searchResults.length,
            itemBuilder: (context, index) {
              final result = searchService.searchResults[index];
              return _buildSearchResultCard(result);
            },
          );
        },
      ),
    );
  }

  Widget _buildSearchResultCard(SearchResult result) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () => _launchUrl(result.url),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                result.title,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF7B1FA2),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                result.url,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                result.content,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.white70,
                ),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

## Authentication System

### Authentication Service

```dart
// lib/services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user_model.dart';
import '../config/app_config.dart';

class AuthService extends ChangeNotifier {
  User? _currentUser;
  String? _token;
  bool _isAuthenticated = false;

  User? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;
  String? get token => _token;

  Future<void> initialize() async {
    await _loadStoredAuth();
  }

  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConfig.authEndpoint}/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        await _setAuthData(data['token'], User.fromJson(data['user']));
        return true;
      }
      return false;
    } catch (e) {
      print('Login error: $e');
      return false;
    }
  }

  Future<bool> signup(String email, String password, String name) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConfig.authEndpoint}/signup'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'name': name,
        }),
      );

      if (response.statusCode == 201) {
        final data = json.decode(response.body);
        await _setAuthData(data['token'], User.fromJson(data['user']));
        return true;
      }
      return false;
    } catch (e) {
      print('Signup error: $e');
      return false;
    }
  }

  Future<void> logout() async {
    _currentUser = null;
    _token = null;
    _isAuthenticated = false;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    await prefs.remove('user_data');
    
    notifyListeners();
  }

  Future<void> _setAuthData(String token, User user) async {
    _token = token;
    _currentUser = user;
    _isAuthenticated = true;
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    await prefs.setString('user_data', json.encode(user.toJson()));
    
    notifyListeners();
  }

  Future<void> _loadStoredAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token');
    final userData = prefs.getString('user_data');
    
    if (token != null && userData != null) {
      _token = token;
      _currentUser = User.fromJson(json.decode(userData));
      _isAuthenticated = true;
      notifyListeners();
    }
  }
}
```

## Build and Deployment

### 1. Environment Configuration

```dart
// lib/config/app_config.dart
class AppConfig {
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:5000',
  );
  
  static const String _searxngUrl = String.fromEnvironment(
    'SEARXNG_URL',
    defaultValue: 'http://localhost:5001',
  );
  
  static const String apiBaseUrl = _baseUrl;
  static const String authEndpoint = '$_baseUrl/api/auth';
  static const String userEndpoint = '$_baseUrl/api/user';
  static const String searchEndpoint = '$_searxngUrl/api/search';
  
  static const Duration apiTimeout = Duration(seconds: 30);
  static bool get isProduction => _baseUrl.contains('golligog.com');
}
```

### 2. Build Commands

```bash
# Development build
flutter run

# Android APK build
flutter build apk --release --dart-define=API_BASE_URL=https://api.golligog.com --dart-define=SEARXNG_URL=https://search.golligog.com

# Android App Bundle build
flutter build appbundle --release --dart-define=API_BASE_URL=https://api.golligog.com --dart-define=SEARXNG_URL=https://search.golligog.com

# iOS build (macOS required)
flutter build ios --release --dart-define=API_BASE_URL=https://api.golligog.com --dart-define=SEARXNG_URL=https://search.golligog.com

# Web build
flutter build web --release --dart-define=API_BASE_URL=https://api.golligog.com --dart-define=SEARXNG_URL=https://search.golligog.com

# Desktop builds
flutter build windows --release
flutter build linux --release  
flutter build macos --release
```

### 3. Platform-Specific Configuration

#### Android Configuration (android/app/build.gradle)
```gradle
android {
    compileSdkVersion 34
    ndkVersion flutter.ndkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    defaultConfig {
        applicationId "com.golligog.search_engine_app"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
    }

    buildTypes {
        release {
            signingConfig signingConfigs.debug
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### iOS Configuration (ios/Runner/Info.plist)
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>golligog.com</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <false/>
            <key>NSExceptionMinimumTLSVersion</key>
            <string>TLSv1.2</string>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
```

## Testing Strategy

### 1. Unit Tests

```dart
// test/services/search_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;
import 'package:search_engine_app/services/searxng_service.dart';

class MockClient extends Mock implements http.Client {}

void main() {
  group('SearchService', () {
    late SearchService searchService;
    late MockClient mockClient;

    setUp(() {
      mockClient = MockClient();
      searchService = SearchService();
    });

    test('should return search results when API call is successful', () async {
      // Arrange
      const query = 'flutter';
      const mockResponse = '''
        {
          "results": [
            {
              "title": "Flutter - Build apps for any screen",
              "url": "https://flutter.dev",
              "content": "Flutter is Google's UI toolkit...",
              "category": "general"
            }
          ]
        }
      ''';

      when(mockClient.get(any, headers: anyNamed('headers')))
          .thenAnswer((_) async => http.Response(mockResponse, 200));

      // Act
      final results = await searchService.search(query: query);

      // Assert
      expect(results, isNotEmpty);
      expect(results.first.title, equals('Flutter - Build apps for any screen'));
    });
  });
}
```

### 2. Widget Tests

```dart
// test/widgets/search_bar_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:search_engine_app/home_page.dart';

void main() {
  group('SearchBar Widget', () {
    testWidgets('should display search hint text', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: HomePage(),
        ),
      );

      expect(find.text('Search anything...'), findsOneWidget);
    });

    testWidgets('should navigate to search results on submit', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: HomePage(),
        ),
      );

      final searchField = find.byType(TextField);
      await tester.enterText(searchField, 'flutter');
      await tester.testTextInput.receiveAction(TextInputAction.search);
      await tester.pumpAndSettle();

      expect(find.byType(SearchResultsPage), findsOneWidget);
    });
  });
}
```

### 3. Integration Tests

```dart
// integration_test/app_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:search_engine_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Integration Tests', () {
    testWidgets('complete search flow', (WidgetTester tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Find and tap search field
      final searchField = find.byType(TextField);
      expect(searchField, findsOneWidget);
      
      await tester.enterText(searchField, 'flutter development');
      await tester.testTextInput.receiveAction(TextInputAction.search);
      await tester.pumpAndSettle();

      // Verify search results page
      expect(find.text('Search: flutter development'), findsOneWidget);
      
      // Wait for results to load
      await tester.pump(const Duration(seconds: 3));
      
      // Verify results are displayed
      expect(find.byType(Card), findsWidgets);
    });
  });
}
```

## Performance Optimization

### 1. Image Caching

```dart
// lib/widgets/cached_network_image_widget.dart
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

class OptimizedNetworkImage extends StatelessWidget {
  final String imageUrl;
  final double? width;
  final double? height;
  final BoxFit fit;

  const OptimizedNetworkImage({
    super.key,
    required this.imageUrl,
    this.width,
    this.height,
    this.fit = BoxFit.cover,
  });

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      width: width,
      height: height,
      fit: fit,
      placeholder: (context, url) => const Center(
        child: CircularProgressIndicator(),
      ),
      errorWidget: (context, url, error) => Container(
        color: Colors.grey[800],
        child: const Icon(
          Icons.error,
          color: Colors.white54,
        ),
      ),
      memCacheWidth: width?.toInt(),
      memCacheHeight: height?.toInt(),
    );
  }
}
```

### 2. Lazy Loading

```dart
// lib/widgets/lazy_loading_list.dart
import 'package:flutter/material.dart';

class LazyLoadingList extends StatefulWidget {
  final List items;
  final Widget Function(BuildContext, int) itemBuilder;
  final VoidCallback? onLoadMore;
  final bool hasMoreData;

  const LazyLoadingList({
    super.key,
    required this.items,
    required this.itemBuilder,
    this.onLoadMore,
    this.hasMoreData = true,
  });

  @override
  State<LazyLoadingList> createState() => _LazyLoadingListState();
}

class _LazyLoadingListState extends State<LazyLoadingList> {
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= 
        _scrollController.position.maxScrollExtent - 200) {
      if (widget.hasMoreData && widget.onLoadMore != null) {
        widget.onLoadMore!();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: _scrollController,
      itemCount: widget.items.length + (widget.hasMoreData ? 1 : 0),
      itemBuilder: (context, index) {
        if (index < widget.items.length) {
          return widget.itemBuilder(context, index);
        } else {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: CircularProgressIndicator(),
            ),
          );
        }
      },
    );
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }
}
```

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Check network connectivity
   - Verify API base URL configuration
   - Ensure backend services are running

2. **Build Failures**
   - Clean build: `flutter clean && flutter pub get`
   - Update dependencies: `flutter pub upgrade`
   - Check platform-specific configurations

3. **Performance Issues**
   - Enable image caching
   - Implement lazy loading
   - Optimize widget rebuilds

4. **Authentication Problems**
   - Clear stored credentials
   - Check token expiration
   - Verify API endpoints

### Debug Commands

```bash
# Flutter doctor check
flutter doctor -v

# Analyze code issues
flutter analyze

# Run tests
flutter test

# Profile performance
flutter run --profile

# Build with verbose output
flutter build apk --verbose
```

This comprehensive Flutter frontend guide covers all aspects of development, from setup and architecture to deployment and troubleshooting, providing a complete reference for building and maintaining the Golligog search application.
