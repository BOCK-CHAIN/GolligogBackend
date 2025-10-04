# SearXNG Technical Documentation
## Golligog Search Engine Implementation

### Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [SearXNG Configuration](#searxng-configuration)
4. [Backend Implementation](#backend-implementation)
5. [Frontend Integration](#frontend-integration)
6. [API Documentation](#api-documentation)
7. [Deployment](#deployment)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Golligog Search Engine is a privacy-focused search platform that leverages SearXNG as its core search engine while providing a modern Flutter-based user interface. The system is designed with Google-only search results to ensure consistent quality while maintaining user privacy.

### Key Features
- **Privacy-First**: No tracking, no data collection, no ads
- **Google-Only Results**: Filtered to show only Google search results without source attribution
- **Modern UI**: Dark theme, responsive design, Google-like interface
- **Multi-Category Search**: General, Images, News, Videos, Scholar
- **Cross-Platform**: Flutter app for mobile and web

### Technology Stack
- **Search Engine**: SearXNG (Privacy-focused metasearch engine)
- **Backend**: Python Flask (API proxy)
- **Frontend**: Flutter (Cross-platform UI)
- **Database**: PostgreSQL (User management)
- **Authentication**: JWT tokens
- **Deployment**: Docker containers

---

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │───▶│  Flask Backend  │───▶│     SearXNG     │
│                 │    │   (Proxy API)   │    │                 │
│  - Search UI    │    │  - CORS Handler │    │  - Google Only  │
│  - Dark Theme   │    │  - Result Filter│    │  - Privacy Meta │
│  - Categories   │    │  - Auth Proxy   │    │  - Multi-Engine │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────▶│  PostgreSQL DB  │◀─────────────┘
                        │                 │
                        │  - User Data    │
                        │  - Search History│
                        │  - Preferences  │
                        └─────────────────┘
```

### Component Breakdown

#### 1. Flutter Frontend (`/flutter/search_engine_app/`)
- **Entry Point**: `lib/main.dart`
- **Authentication**: `lib/auth_wrapper.dart`, `lib/login_page.dart`, `lib/signup_page.dart`
- **Search Interface**: `lib/search_results_page.dart`
- **Services**: `lib/services/searxng_service.dart`, `lib/services/auth_service.dart`
- **Models**: `lib/models/search_models.dart`

#### 2. Flask Backend (`/backend/`)
- **Main Server**: `searxng_proxy.py`
- **Purpose**: API proxy between Flutter and SearXNG
- **Features**: CORS handling, result filtering, Google-only enforcement

#### 3. SearXNG Instance (`/searxng/`)
- **Configuration**: `searx/settings.yml`
- **Customization**: Google-only engines enabled
- **Privacy**: No logging, no tracking

#### 4. Database Layer (`/server/`)
- **Technology**: PostgreSQL with Sequelize ORM
- **Purpose**: User management, authentication, search history

---

## SearXNG Configuration

### Engine Configuration (`/searxng/searx/settings.yml`)

The SearXNG instance is configured to use only Google engines for consistent search results:

```yaml
# Enabled Google Engines
engines:
  - name: google
    engine: google
    shortcut: go
    disabled: false

  - name: google images
    engine: google_images
    shortcut: goi
    disabled: false

  - name: google news
    engine: google_news
    shortcut: gon
    disabled: false

  - name: google videos
    engine: google_videos
    shortcut: gov
    disabled: false

  - name: google scholar
    engine: google_scholar
    shortcut: gos
    disabled: false

  # All other engines disabled
  - name: bing
    engine: bing
    disabled: true
  # ... (200+ other engines disabled)
```

### Custom Settings

```yaml
general:
  instance_name: "Golligog"
  debug: false
  enable_metrics: true

search:
  safe_search: 0
  autocomplete: ""
  favicon_resolver: ""
  default_lang: "auto"

ui:
  static_use_hash: true
  default_theme: dark
  center_alignment: true
```

### Google-Only Configuration Script

A Python script (`configure_google_only.py`) automatically configures SearXNG:

```python
def configure_google_only():
    google_engines = {
        'google', 'google images', 'google news',
        'google videos', 'google scholar'
    }
    
    # Disable all non-Google engines
    for engine in settings['engines']:
        if engine['name'] in google_engines:
            engine['disabled'] = False
        else:
            engine['disabled'] = True
```

---

## Backend Implementation

### Flask Proxy Server (`backend/searxng_proxy.py`)

#### Core Functionality

```python
@app.route('/api/search', methods=['GET'])
def search():
    """Google-only search with source filtering"""
    
    # Map categories to Google engines
    google_engines_map = {
        'general': 'google',
        'images': 'google_images',
        'news': 'google_news', 
        'videos': 'google_videos',
        'science': 'google_scholar',
        'files': 'google_scholar',
        'map': 'google',
    }
    
    # Force Google engine based on category
    selected_engine = google_engines_map.get(category, 'google')
    
    params = {
        'q': query,
        'format': 'json',
        'engines': selected_engine,  # Force Google only
        'lang': 'en',
        'pageno': page,
    }
```

#### Source Information Filtering

```python
def filter_result_sources(result_data):
    """Remove provider/source information"""
    
    filtered_results = []
    for result in result_data['results']:
        clean_result = {
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'publishedDate': result.get('publishedDate'),
            'thumbnail': result.get('thumbnail'),
            # Removed: engine, provider, source fields
        }
        filtered_results.append(clean_result)
    
    # Remove engine metadata
    if 'engines' in result_data:
        del result_data['engines']
    
    return result_data
```

#### Fallback System

```python
# Primary: Local SearXNG instance
result = search_with_instance(SEARXNG_BASE_URL, params)

# Fallback: Public SearXNG instances
PUBLIC_INSTANCES = [
    'https://search.sapti.me',
    'https://searx.be',
    'https://searx.info',
    'https://search.mdosch.de',
    'https://searx.tiekoetter.com',
]

if not result:
    for instance in PUBLIC_INSTANCES:
        result = search_with_instance(instance, params)
        if result:
            break
```

### API Endpoints

| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/search` | GET | Search proxy | `q`, `category`, `page`, `lang` |
| `/api/engines` | GET | Available engines | None |
| `/api/health` | GET | Health check | None |
| `/` | GET | API info | None |

---

## Frontend Integration

### Search Service (`lib/services/searxng_service.dart`)

```dart
class SearXNGService {
  static const String _baseUrl = 'http://localhost:5000/api';

  Future<SearchResponse> search({
    required String query,
    String category = 'general',
    int page = 1,
    String lang = 'en',
  }) async {
    
    final uri = Uri.parse('$_baseUrl/search').replace(
      queryParameters: {
        'q': query,
        'category': category,
        'page': page.toString(),
        'lang': lang,
      },
    );

    final response = await http.get(uri);
    
    if (response.statusCode == 200) {
      final jsonData = json.decode(response.body);
      return SearchResponse.fromJson(jsonData);
    } else {
      throw Exception('Search failed: ${response.statusCode}');
    }
  }
}
```

### Search Results Display

#### Category-Based Search

```dart
Widget _buildCategoryButton(String label, String category) {
  final isSelected = _currentCategory == category;
  return TextButton(
    onPressed: () => _performSearch(_searchController.text, category: category),
    child: Text(
      label,
      style: TextStyle(
        color: isSelected ? Color(0xFF7B1FA2) : Colors.white70,
      ),
    ),
  );
}
```

#### Result Cards

```dart
Widget _buildRealSearchResult(SearchResult result, int index) {
  return Container(
    margin: EdgeInsets.only(bottom: 20),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // URL (no provider shown)
        Text(
          result.url,
          style: TextStyle(color: Color(0xFF4CAF50), fontSize: 14),
        ),
        
        // Title (clickable)
        GestureDetector(
          onTap: () => _launchURL(result.url),
          child: Text(
            result.title,
            style: TextStyle(
              color: Color(0xFF7B1FA2),  // Purple theme
              fontSize: 20,
              decoration: TextDecoration.underline,
            ),
          ),
        ),
        
        // Content/Description
        Text(
          result.content,
          style: TextStyle(color: Colors.white70, fontSize: 14),
          maxLines: 3,
          overflow: TextOverflow.ellipsis,
        ),
      ],
    ),
  );
}
```

### Dark Theme Implementation

```dart
MaterialApp(
  theme: ThemeData(
    brightness: Brightness.dark,
    primarySwatch: Colors.deepPurple,
    scaffoldBackgroundColor: Color(0xFF121212),
    cardColor: Color(0xFF1E1E1E),
    textTheme: TextTheme(
      bodyLarge: TextStyle(color: Colors.white),
      bodyMedium: TextStyle(color: Colors.white70),
    ),
  ),
)
```

---

## API Documentation

### Search API

#### Request
```http
GET /api/search?q=flutter&category=general&page=1&lang=en
```

#### Response
```json
{
  "query": "flutter",
  "number_of_results": 42,
  "results": [
    {
      "title": "Flutter - Build apps for any screen",
      "url": "https://flutter.dev/",
      "content": "Flutter is Google's UI toolkit for building natively compiled applications...",
      "thumbnail": "https://flutter.dev/images/flutter-logo.png",
      "publishedDate": null
    }
  ],
  "suggestions": ["flutter framework", "flutter tutorial"],
  "corrections": null
}
```

### Health Check API

#### Request
```http
GET /api/health
```

#### Response
```json
{
  "status": "healthy",
  "local_instance": true,
  "public_instances_available": true,
  "searxng_url": "http://localhost:8080"
}
```

---

## Deployment

### Local Development

1. **Start SearXNG**:
```bash
cd searxng
python manage searxng run
```

2. **Start Flask Backend**:
```bash
cd backend
python3 searxng_proxy.py
```

3. **Start Flutter App**:
```bash
cd flutter/search_engine_app
flutter run
```

### Docker Deployment

#### SearXNG Container
```dockerfile
FROM searxng/searxng:latest
COPY searx/settings.yml /etc/searxng/settings.yml
EXPOSE 8080
```

#### Flask Backend Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "searxng_proxy.py"]
```

### Production Considerations

1. **Environment Variables**:
```bash
SEARXNG_URL=http://searxng:8080
FLASK_ENV=production
DEBUG=false
```

2. **Reverse Proxy** (Nginx):
```nginx
upstream flask_backend {
    server localhost:5000;
}

upstream searxng {
    server localhost:8080;
}

server {
    listen 80;
    server_name golligog.com;
    
    location /api/ {
        proxy_pass http://flask_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://searxng;
    }
}
```

---

## Security Considerations

### Privacy Protection

1. **No Logging**: SearXNG configured with no search logging
2. **No Tracking**: No cookies or session tracking in search
3. **Source Masking**: Provider information stripped from results
4. **HTTPS Only**: All communications encrypted in production

### API Security

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/search')
@limiter.limit("10 per minute")
def search():
    # Rate-limited search endpoint
```

### Input Validation

```python
from flask import request, jsonify
import re

def validate_query(query):
    if not query or len(query.strip()) == 0:
        return False, "Query cannot be empty"
    
    if len(query) > 500:
        return False, "Query too long"
    
    # Prevent injection attacks
    if re.search(r'[<>"\';]', query):
        return False, "Invalid characters in query"
    
    return True, None

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip()
    valid, error = validate_query(query)
    
    if not valid:
        return jsonify({'error': error}), 400
```

---

## Performance Optimization

### Caching Strategy

1. **Backend Caching**:
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@app.route('/api/search')
@cache.memoize(timeout=300)  # 5 minutes
def search():
    # Cached search results
```

2. **Frontend Caching**:
```dart
class SearchCache {
  static final Map<String, SearchResponse> _cache = {};
  static const Duration _expiry = Duration(minutes: 5);
  
  static SearchResponse? get(String key) {
    final cached = _cache[key];
    if (cached != null && _isValid(key)) {
      return cached;
    }
    return null;
  }
  
  static void set(String key, SearchResponse response) {
    _cache[key] = response;
  }
}
```

### Database Optimization

```sql
-- Indexes for user management
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_timestamp ON search_history(created_at);

-- Partitioning for large datasets
CREATE TABLE search_history_2024 PARTITION OF search_history
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### SearXNG Performance

```yaml
# settings.yml optimizations
server:
  limiter: true
  port: 8080
  bind_address: "0.0.0.0"
  
redis:
  url: redis://localhost:6379/0
  
ui:
  static_use_hash: true
  infinite_scroll: true
  query_in_title: true
```

---

## Troubleshooting

### Common Issues

#### 1. SearXNG Connection Failed
**Symptoms**: "All search instances are unavailable"

**Solutions**:
```bash
# Check SearXNG status
curl http://localhost:8080/healthz

# Restart SearXNG
cd searxng
python manage searxng restart

# Check logs
tail -f searxng/local/searxng.log
```

#### 2. Flutter Build Issues
**Symptoms**: Build failures, dependency conflicts

**Solutions**:
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# Check Flutter doctor
flutter doctor -v
```

#### 3. Backend API Errors
**Symptoms**: 500 errors, timeout issues

**Solutions**:
```bash
# Check backend logs
tail -f backend/logs/app.log

# Test API directly
curl "http://localhost:5000/api/search?q=test"

# Check Python dependencies
pip install -r backend/requirements.txt
```

### Debug Mode

#### Enable Debug Logging
```python
# searxng_proxy.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app.logger.setLevel(logging.DEBUG)
```

#### Flutter Debug
```dart
// Enable debug prints
void debugSearch(String message) {
  if (kDebugMode) {
    print('SEARCH_DEBUG: $message');
  }
}
```

### Performance Monitoring

#### Backend Metrics
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('golligog_backend', 'Golligog Backend API')

@metrics.counter('search_requests_total', 'Total search requests')
@app.route('/api/search')
def search():
    # Monitored search endpoint
```

#### Health Checks
```bash
# Automated health monitoring
#!/bin/bash
while true; do
    if ! curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "Backend unhealthy, restarting..."
        systemctl restart golligog-backend
    fi
    sleep 30
done
```

---

## Configuration Files Reference

### SearXNG Settings (`searxng/searx/settings.yml`)
- **Location**: `/home/kali/search_engine/searxng/searx/settings.yml`
- **Purpose**: Main SearXNG configuration
- **Key Settings**: Engine configuration, UI themes, privacy settings

### Flask Backend (`backend/searxng_proxy.py`)
- **Location**: `/home/kali/search_engine/backend/searxng_proxy.py`
- **Purpose**: API proxy server
- **Key Features**: CORS, rate limiting, result filtering

### Flutter App (`flutter/search_engine_app/`)
- **Configuration**: `pubspec.yaml`
- **Services**: API clients in `lib/services/`
- **Models**: Data structures in `lib/models/`

### Database Schema (`server/`)
- **Users Table**: Authentication and profile data
- **Search History**: User search patterns
- **Preferences**: User customization settings

---

This documentation provides a comprehensive technical overview of the Golligog Search Engine implementation using SearXNG. The system is designed for privacy, performance, and user experience while maintaining the familiar Google search interface that users expect.
