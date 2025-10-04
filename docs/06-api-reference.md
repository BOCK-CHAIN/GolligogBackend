# API Reference Guide

## Overview

This document provides comprehensive API documentation for the Golligog Search Engine, covering all endpoints, request/response formats, authentication, and integration examples.

## Base URLs

- **Production**: `https://api.golligog.com`
- **Development**: `http://localhost:5000`
- **Search Service**: `https://search.golligog.com` (Production) | `http://localhost:5001` (Development)

## Authentication

### JWT Token Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

### Token Structure

```json
{
  "userId": "user_id_here",
  "email": "user@example.com",
  "iat": 1640995200,
  "exp": 1641081600
}
```

## Authentication Endpoints

### POST /api/auth/signup

Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "User already exists"
}
```

---

### POST /api/auth/login

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

---

### POST /api/auth/logout

Logout user and invalidate token.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

---

### GET /api/auth/verify

Verify JWT token validity.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "valid": true,
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "valid": false,
  "error": "Invalid or expired token"
}
```

## User Management Endpoints

### GET /api/user/profile

Get current user profile information.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user_123",
      "name": "John Doe",
      "email": "john@example.com",
      "createdAt": "2024-01-01T00:00:00.000Z",
      "searchCount": 150,
      "lastLogin": "2024-01-15T10:30:00.000Z"
    }
  }
}
```

---

### PUT /api/user/profile

Update user profile information.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "data": {
    "user": {
      "id": "user_123",
      "name": "John Smith",
      "email": "johnsmith@example.com",
      "updatedAt": "2024-01-15T10:35:00.000Z"
    }
  }
}
```

---

### POST /api/user/change-password

Change user password.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "currentPassword": "oldPassword123",
  "newPassword": "newSecurePassword456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Current password is incorrect"
}
```

---

### DELETE /api/user/account

Delete user account permanently.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "password": "currentPassword123",
  "confirmation": "DELETE_MY_ACCOUNT"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Account deleted successfully"
}
```

## Search History Endpoints

### GET /api/user/search-history

Get user's search history with pagination.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)
- `category` (optional): Filter by search category
- `startDate` (optional): Filter from date (ISO 8601)
- `endDate` (optional): Filter to date (ISO 8601)

**Example Request:**
```http
GET /api/user/search-history?page=1&limit=10&category=general
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "searches": [
      {
        "id": "search_456",
        "query": "flutter development",
        "category": "general",
        "timestamp": "2024-01-15T10:30:00.000Z",
        "resultCount": 25
      },
      {
        "id": "search_455",
        "query": "react native vs flutter",
        "category": "general",
        "timestamp": "2024-01-15T09:15:00.000Z",
        "resultCount": 18
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalResults": 48,
      "hasNextPage": true,
      "hasPreviousPage": false
    }
  }
}
```

---

### POST /api/user/search-history

Save a search query to user's history.

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "python web scraping",
  "category": "general",
  "resultCount": 32
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Search saved to history",
  "data": {
    "search": {
      "id": "search_457",
      "query": "python web scraping",
      "category": "general",
      "timestamp": "2024-01-15T11:00:00.000Z",
      "resultCount": 32
    }
  }
}
```

---

### DELETE /api/user/search-history/:searchId

Delete a specific search from history.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**URL Parameters:**
- `searchId`: ID of the search to delete

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Search deleted from history"
}
```

---

### DELETE /api/user/search-history

Clear all search history for the user.

**Headers:**
```http
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Search history cleared successfully"
}
```

## Search API Endpoints

### GET /search

Perform a search query using SearXNG.

**Base URL:** `https://search.golligog.com` (or `http://localhost:5001` for development)

**Query Parameters:**
- `q` (required): Search query string
- `category` (optional): Search category (default: 'general')
  - Supported categories: `general`, `images`, `news`, `videos`, `music`, `it`, `science`
- `page` (optional): Page number (default: 1)
- `format` (optional): Response format (default: 'json')
- `lang` (optional): Language code (default: 'en')

**Example Request:**
```http
GET /search?q=flutter%20development&category=general&page=1&format=json
```

**Response (200 OK):**
```json
{
  "query": "flutter development",
  "category": "general",
  "page": 1,
  "results": [
    {
      "title": "Flutter - Build apps for any screen",
      "url": "https://flutter.dev/",
      "content": "Flutter is Google's UI toolkit for building beautiful, natively compiled applications for mobile, web, and desktop from a single codebase.",
      "thumbnail": "https://flutter.dev/assets/images/flutter-logo.png",
      "publishedDate": "2024-01-10",
      "category": "general",
      "score": 0.95
    },
    {
      "title": "Flutter Tutorial for Beginners",
      "url": "https://example.com/flutter-tutorial",
      "content": "Learn Flutter development from scratch with this comprehensive tutorial covering widgets, state management, and more.",
      "thumbnail": null,
      "publishedDate": "2024-01-12",
      "category": "general",
      "score": 0.88
    }
  ],
  "totalResults": 847,
  "resultsPerPage": 20,
  "searchTime": 0.234,
  "suggestions": [
    "flutter tutorial",
    "flutter vs react native",
    "flutter web development"
  ]
}
```

---

### GET /search/suggestions

Get search suggestions based on partial query.

**Query Parameters:**
- `q` (required): Partial search query
- `limit` (optional): Maximum suggestions (default: 5, max: 10)

**Example Request:**
```http
GET /search/suggestions?q=flutter&limit=5
```

**Response (200 OK):**
```json
{
  "query": "flutter",
  "suggestions": [
    "flutter development",
    "flutter tutorial",
    "flutter vs react native",
    "flutter web",
    "flutter state management"
  ]
}
```

---

### GET /search/categories

Get available search categories.

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": "general",
      "name": "General",
      "description": "General web search results"
    },
    {
      "id": "images",
      "name": "Images",
      "description": "Image search results"
    },
    {
      "id": "news",
      "name": "News",
      "description": "News articles and current events"
    },
    {
      "id": "videos",
      "name": "Videos",
      "description": "Video content from various platforms"
    },
    {
      "id": "music",
      "name": "Music",
      "description": "Music and audio content"
    },
    {
      "id": "it",
      "name": "IT",
      "description": "Information technology and programming"
    },
    {
      "id": "science",
      "name": "Science",
      "description": "Scientific articles and research"
    }
  ]
}
```

## Health Check Endpoints

### GET /health

Basic health check for the main API server.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "version": "1.0.0",
  "uptime": 86400,
  "services": {
    "database": "healthy",
    "redis": "healthy"
  }
}
```

---

### GET /search/health

Health check for the search service.

**Base URL:** `https://search.golligog.com` (or `http://localhost:5001`)

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "searxng": {
    "status": "operational",
    "responseTime": 150
  }
}
```

## Error Handling

### Standard Error Response Format

All API endpoints return errors in the following format:

```json
{
  "success": false,
  "error": "Error message description",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-15T11:00:00.000Z",
  "path": "/api/endpoint"
}
```

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request parameters or body
- **401 Unauthorized**: Authentication required or invalid token
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

### Common Error Codes

- `INVALID_CREDENTIALS`: Login credentials are incorrect
- `USER_EXISTS`: User already exists during signup
- `TOKEN_EXPIRED`: JWT token has expired
- `TOKEN_INVALID`: JWT token is malformed or invalid
- `VALIDATION_ERROR`: Request validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests from client
- `SEARCH_SERVICE_UNAVAILABLE`: Search service is down
- `DATABASE_ERROR`: Database connection or query error

## Rate Limiting

### Rate Limit Headers

All responses include rate limiting headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642247400
```

### Rate Limits

- **Authentication endpoints**: 5 requests per minute per IP
- **Search endpoints**: 60 requests per minute per user
- **User profile endpoints**: 30 requests per minute per user
- **General endpoints**: 100 requests per minute per user

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "retryAfter": 60,
  "limit": 100,
  "remaining": 0,
  "reset": 1642247400
}
```

## SDK and Integration Examples

### JavaScript/Node.js SDK

```javascript
class GolligogAPI {
  constructor(baseURL = 'https://api.golligog.com', searchURL = 'https://search.golligog.com') {
    this.baseURL = baseURL;
    this.searchURL = searchURL;
    this.token = null;
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();
    if (data.success) {
      this.token = data.data.token;
    }
    return data;
  }

  async search(query, options = {}) {
    const params = new URLSearchParams({
      q: query,
      category: options.category || 'general',
      page: options.page || 1,
      format: 'json',
    });

    const response = await fetch(`${this.searchURL}/search?${params}`);
    return await response.json();
  }

  async getProfile() {
    const response = await fetch(`${this.baseURL}/api/user/profile`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
    return await response.json();
  }

  async getSearchHistory(page = 1, limit = 20) {
    const params = new URLSearchParams({ page, limit });
    const response = await fetch(`${this.baseURL}/api/user/search-history?${params}`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });
    return await response.json();
  }
}

// Usage example
const api = new GolligogAPI();

// Login
await api.login('user@example.com', 'password123');

// Search
const searchResults = await api.search('flutter development', {
  category: 'general',
  page: 1
});

// Get user profile
const profile = await api.getProfile();

// Get search history
const history = await api.getSearchHistory(1, 10);
```

### Python SDK

```python
import requests
from typing import Optional, Dict, Any

class GolligogAPI:
    def __init__(self, base_url: str = 'https://api.golligog.com', 
                 search_url: str = 'https://search.golligog.com'):
        self.base_url = base_url
        self.search_url = search_url
        self.token: Optional[str] = None

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and store JWT token"""
        response = requests.post(
            f'{self.base_url}/api/auth/login',
            json={'email': email, 'password': password}
        )
        data = response.json()
        if data.get('success'):
            self.token = data['data']['token']
        return data

    def search(self, query: str, category: str = 'general', 
               page: int = 1) -> Dict[str, Any]:
        """Perform search query"""
        params = {
            'q': query,
            'category': category,
            'page': page,
            'format': 'json'
        }
        response = requests.get(f'{self.search_url}/search', params=params)
        return response.json()

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile"""
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(f'{self.base_url}/api/user/profile', headers=headers)
        return response.json()

    def get_search_history(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get user search history"""
        headers = {'Authorization': f'Bearer {self.token}'}
        params = {'page': page, 'limit': limit}
        response = requests.get(
            f'{self.base_url}/api/user/search-history', 
            headers=headers, 
            params=params
        )
        return response.json()

# Usage example
api = GolligogAPI()

# Login
login_result = api.login('user@example.com', 'password123')

# Search
search_results = api.search('python tutorials', category='general', page=1)

# Get profile
profile = api.get_profile()

# Get search history
history = api.get_search_history(page=1, limit=10)
```

### cURL Examples

#### Login
```bash
curl -X POST https://api.golligog.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

#### Search
```bash
curl "https://search.golligog.com/search?q=flutter%20development&category=general&page=1&format=json"
```

#### Get Profile
```bash
curl https://api.golligog.com/api/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Get Search History
```bash
curl "https://api.golligog.com/api/user/search-history?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## WebSocket API (Real-time Features)

### Connection

Connect to WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('wss://api.golligog.com/ws');

// Authenticate after connection
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};
```

### Search Suggestions in Real-time

```javascript
// Send search query for suggestions
ws.send(JSON.stringify({
  type: 'search_suggestions',
  query: 'flutter'
}));

// Receive suggestions
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'search_suggestions') {
    console.log('Suggestions:', data.suggestions);
  }
};
```

## Testing the API

### Postman Collection

Import the following Postman collection for testing:

```json
{
  "info": {
    "name": "Golligog API",
    "description": "Complete API collection for Golligog Search Engine"
  },
  "auth": {
    "type": "bearer",
    "bearer": [
      {
        "key": "token",
        "value": "{{jwt_token}}",
        "type": "string"
      }
    ]
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.golligog.com"
    },
    {
      "key": "search_url", 
      "value": "https://search.golligog.com"
    },
    {
      "key": "jwt_token",
      "value": ""
    }
  ]
}
```

### API Testing Script

```bash
#!/bin/bash

# Test script for Golligog API
BASE_URL="https://api.golligog.com"
SEARCH_URL="https://search.golligog.com"

echo "Testing Golligog API..."

# Test health endpoints
echo "1. Testing health endpoints..."
curl -s "$BASE_URL/health" | jq '.'
curl -s "$SEARCH_URL/health" | jq '.'

# Test search without authentication
echo "2. Testing search endpoint..."
curl -s "$SEARCH_URL/search?q=test&category=general&format=json" | jq '.results[0]'

# Test authentication
echo "3. Testing authentication..."
TOKEN=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass"}' | jq -r '.data.token')

if [ "$TOKEN" != "null" ]; then
  echo "Login successful, token: ${TOKEN:0:20}..."
  
  # Test profile endpoint
  echo "4. Testing profile endpoint..."
  curl -s "$BASE_URL/api/user/profile" \
    -H "Authorization: Bearer $TOKEN" | jq '.data.user'
    
  # Test search history
  echo "5. Testing search history..."
  curl -s "$BASE_URL/api/user/search-history?limit=5" \
    -H "Authorization: Bearer $TOKEN" | jq '.data.searches'
else
  echo "Login failed"
fi

echo "API testing completed."
```

This comprehensive API reference guide provides all the information needed to integrate with the Golligog Search Engine API, including authentication, search functionality, user management, and real-time features.
