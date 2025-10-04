# Backend Development

## Node.js Authentication Server

### Project Structure
```
server/
├── server.js                 # Main server entry point
├── package.json              # Dependencies and scripts
├── .env                      # Environment variables (local)
├── .env.example              # Environment template
├── prisma/
│   ├── schema.prisma         # Database schema definition
│   └── migrations/           # Database migration files
├── routes/
│   ├── auth.js               # Authentication endpoints
│   ├── user.js               # User management endpoints
│   └── health.js             # Health check endpoints
├── middleware/
│   ├── auth.js               # JWT authentication middleware
│   ├── validation.js         # Request validation middleware
│   └── rateLimit.js          # Rate limiting configuration
├── services/
│   ├── authService.js        # Authentication business logic
│   ├── userService.js        # User management logic
│   └── tokenService.js       # JWT token management
└── utils/
    ├── database.js           # Database utilities
    ├── logger.js             # Logging configuration
    └── errors.js             # Custom error classes
```

### Core Dependencies

#### Essential Packages
```json
{
  "dependencies": {
    "@prisma/client": "^6.15.0",      // Database ORM client
    "express": "^4.21.2",             // Web framework
    "bcryptjs": "^2.4.3",             // Password hashing
    "jsonwebtoken": "^9.0.2",         // JWT authentication
    "cors": "^2.8.5",                 // Cross-origin requests
    "helmet": "^7.2.0",               // Security headers
    "express-rate-limit": "^6.11.2",  // Rate limiting
    "express-validator": "^7.0.1",    // Input validation
    "dotenv": "^16.4.5",              // Environment variables
    "winston": "^3.10.0"              // Logging framework
  },
  "devDependencies": {
    "nodemon": "^3.0.1",              // Development server
    "jest": "^29.7.0",                // Testing framework
    "supertest": "^6.3.3",            // HTTP testing
    "prisma": "^6.15.0"               // Database toolkit
  }
}
```

### Database Schema (Prisma)

#### Schema Definition
```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  password  String
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  
  // Relationships
  searchHistory SearchHistory[]
  sessions      UserSession[]
  
  @@map("users")
}

model SearchHistory {
  id          Int      @id @default(autoincrement())
  userId      Int      @map("user_id")
  query       String
  category    String   @default("general")
  resultCount Int?     @map("result_count")
  createdAt   DateTime @default(now()) @map("created_at")
  
  // Relationships
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("search_history")
  @@index([userId, createdAt])
}

model UserSession {
  id        Int      @id @default(autoincrement())
  userId    Int      @map("user_id")
  tokenHash String   @map("token_hash")
  expiresAt DateTime @map("expires_at")
  createdAt DateTime @default(now()) @map("created_at")
  
  // Relationships
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("user_sessions")
  @@index([tokenHash])
  @@index([expiresAt])
}
```

### Authentication Implementation

#### JWT Service
```javascript
// services/tokenService.js
const jwt = require('jsonwebtoken');
const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

class TokenService {
  static generateTokens(userId) {
    const payload = { userId };
    
    const accessToken = jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '15m' }
    );
    
    const refreshToken = jwt.sign(
      payload,
      process.env.JWT_REFRESH_SECRET,
      { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' }
    );
    
    return { accessToken, refreshToken };
  }
  
  static async storeRefreshToken(userId, refreshToken) {
    const tokenHash = await bcrypt.hash(refreshToken, 10);
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days
    
    return await prisma.userSession.create({
      data: {
        userId,
        tokenHash,
        expiresAt
      }
    });
  }
  
  static async validateRefreshToken(refreshToken) {
    try {
      const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
      
      const sessions = await prisma.userSession.findMany({
        where: {
          userId: payload.userId,
          expiresAt: { gt: new Date() }
        }
      });
      
      for (const session of sessions) {
        const isValid = await bcrypt.compare(refreshToken, session.tokenHash);
        if (isValid) {
          return payload;
        }
      }
      
      return null;
    } catch (error) {
      return null;
    }
  }
  
  static async revokeRefreshToken(refreshToken) {
    const sessions = await prisma.userSession.findMany({
      where: {
        expiresAt: { gt: new Date() }
      }
    });
    
    for (const session of sessions) {
      const isMatch = await bcrypt.compare(refreshToken, session.tokenHash);
      if (isMatch) {
        await prisma.userSession.delete({
          where: { id: session.id }
        });
        return true;
      }
    }
    
    return false;
  }
}

module.exports = TokenService;
```

#### Authentication Routes
```javascript
// routes/auth.js
const express = require('express');
const bcrypt = require('bcryptjs');
const { body, validationResult } = require('express-validator');
const { PrismaClient } = require('@prisma/client');
const TokenService = require('../services/tokenService');

const router = express.Router();
const prisma = new PrismaClient();

// Register endpoint
router.post('/register', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 6 }),
  body('name').optional().trim().escape()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: 'Validation failed',
        errors: errors.array()
      });
    }
    
    const { email, password, name } = req.body;
    
    // Check if user exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });
    
    if (existingUser) {
      return res.status(409).json({
        message: 'User with this email already exists'
      });
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 12);
    
    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name: name || null
      }
    });
    
    // Generate tokens
    const { accessToken, refreshToken } = TokenService.generateTokens(user.id);
    await TokenService.storeRefreshToken(user.id, refreshToken);
    
    res.status(201).json({
      message: 'User created successfully',
      token: accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt
      }
    });
    
  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      message: 'Internal server error'
    });
  }
});

// Login endpoint
router.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').notEmpty()
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        message: 'Validation failed',
        errors: errors.array()
      });
    }
    
    const { email, password } = req.body;
    
    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    });
    
    if (!user) {
      return res.status(401).json({
        message: 'Invalid credentials'
      });
    }
    
    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({
        message: 'Invalid credentials'
      });
    }
    
    // Generate tokens
    const { accessToken, refreshToken } = TokenService.generateTokens(user.id);
    await TokenService.storeRefreshToken(user.id, refreshToken);
    
    res.json({
      message: 'Login successful',
      token: accessToken,
      refreshToken,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        createdAt: user.createdAt
      }
    });
    
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      message: 'Internal server error'
    });
  }
});

module.exports = router;
```

## Python Search Proxy

### Project Structure
```
backend/
├── searxng_proxy.py          # Main Flask application
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── utils/
│   ├── search_filter.py      # Result filtering utilities
│   ├── response_formatter.py # Response formatting
│   └── rate_limiter.py       # Rate limiting for searches
└── tests/
    ├── test_proxy.py         # Unit tests
    └── test_integration.py   # Integration tests
```

### Dependencies
```txt
# requirements.txt
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
redis==4.6.0
ratelimit==2.2.1
```

### Flask Proxy Implementation

#### Main Application
```python
# searxng_proxy.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration
CORS(app, origins=[
    "http://localhost:3000",
    "https://golligog.com",
    "https://www.golligog.com"
], supports_credentials=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SEARXNG_URL = os.getenv('SEARXNG_URL', 'http://localhost:8080')
PROXY_PORT = int(os.getenv('PROXY_PORT', 5001))
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))

class SearchProxy:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Golligog-Search-Proxy/1.0'
        })
    
    def search(self, query, category='general', page=1, lang='en'):
        """
        Proxy search request to SearXNG and filter results
        """
        try:
            params = {
                'q': query,
                'category': category,
                'page': page,
                'lang': lang,
                'format': 'json'
            }
            
            logger.info(f"Search request: {query} (category: {category})")
            
            response = self.session.get(
                f"{SEARXNG_URL}/search",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                filtered_results = self._filter_results(results)
                return filtered_results
            else:
                logger.error(f"SearXNG error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Search request timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Search request error: {e}")
            return None
    
    def _filter_results(self, results):
        """
        Filter and clean search results
        """
        if not results or 'results' not in results:
            return {
                'query': '',
                'number_of_results': 0,
                'results': [],
                'search_time': 0
            }
        
        filtered_results = []
        
        for result in results.get('results', []):
            # Remove provider/engine information
            filtered_result = {
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content': result.get('content', ''),
                'publishedDate': result.get('publishedDate'),
                'img_src': result.get('img_src'),
                'thumbnail': result.get('thumbnail')
            }
            
            # Remove empty fields
            filtered_result = {k: v for k, v in filtered_result.items() if v}
            filtered_results.append(filtered_result)
        
        return {
            'query': results.get('query', ''),
            'number_of_results': len(filtered_results),
            'results': filtered_results,
            'search_time': results.get('search_time', 0),
            'timestamp': datetime.now().isoformat()
        }

# Initialize search proxy
search_proxy = SearchProxy()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test SearXNG connectivity
        response = requests.get(f"{SEARXNG_URL}/config", timeout=5)
        searxng_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        searxng_status = "unhealthy"
    
    return jsonify({
        "status": "healthy",
        "searxng": searxng_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/search', methods=['GET'])
def search():
    """Main search endpoint"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'error': 'Query parameter "q" is required'
            }), 400
        
        category = request.args.get('category', 'general')
        page = int(request.args.get('page', 1))
        lang = request.args.get('lang', 'en')
        
        # Validate parameters
        if page < 1:
            page = 1
        if len(query) > 500:
            return jsonify({
                'error': 'Query too long (max 500 characters)'
            }), 400
        
        # Perform search
        results = search_proxy.search(query, category, page, lang)
        
        if results is None:
            return jsonify({
                'error': 'Search service temporarily unavailable'
            }), 503
        
        return jsonify(results)
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    """Search suggestions endpoint"""
    try:
        query = request.args.get('q', '').strip()
        if not query or len(query) < 2:
            return jsonify({'suggestions': []})
        
        # You can implement autocomplete suggestions here
        # For now, return empty array
        return jsonify({'suggestions': []})
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return jsonify({'suggestions': []})

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=PROXY_PORT,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
```

### Security & Performance

#### Rate Limiting
```python
# utils/rate_limiter.py
from functools import wraps
from flask import request, jsonify, g
import time
import redis
import hashlib

# Redis connection for rate limiting
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

def rate_limit(max_requests=60, window=60):
    """
    Rate limiting decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            client_id = hashlib.md5(f"{client_ip}{user_agent}".encode()).hexdigest()
            
            # Rate limit key
            key = f"rate_limit:{client_id}"
            
            try:
                current_requests = redis_client.get(key)
                if current_requests is None:
                    # First request in window
                    redis_client.setex(key, window, 1)
                elif int(current_requests) >= max_requests:
                    # Rate limit exceeded
                    return jsonify({
                        'error': 'Rate limit exceeded. Try again later.',
                        'retry_after': redis_client.ttl(key)
                    }), 429
                else:
                    # Increment counter
                    redis_client.incr(key)
                
            except redis.RedisError:
                # If Redis is down, allow request but log error
                logger.warning("Redis connection failed for rate limiting")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Apply rate limiting to search endpoint
@app.route('/api/search', methods=['GET'])
@rate_limit(max_requests=60, window=60)  # 60 requests per minute
def search():
    # ... search implementation
```

### Testing

#### Unit Tests
```python
# tests/test_proxy.py
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from searxng_proxy import app, SearchProxy

class TestSearchProxy(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
    
    @patch('searxng_proxy.search_proxy.search')
    def test_search_endpoint(self, mock_search):
        """Test search endpoint with valid query"""
        mock_search.return_value = {
            'query': 'test query',
            'number_of_results': 1,
            'results': [{'title': 'Test Result', 'url': 'https://example.com'}],
            'search_time': 0.5
        }
        
        response = self.app.get('/api/search?q=test%20query')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['query'], 'test query')
        self.assertEqual(data['number_of_results'], 1)
    
    def test_search_no_query(self):
        """Test search endpoint without query parameter"""
        response = self.app.get('/api/search')
        self.assertEqual(response.status_code, 400)
        
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_search_empty_query(self):
        """Test search endpoint with empty query"""
        response = self.app.get('/api/search?q=')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
```

### Deployment Configuration

#### Environment Variables
```bash
# .env
SEARXNG_URL=http://localhost:8080
PROXY_PORT=5001
FLASK_ENV=production
RATE_LIMIT_PER_MINUTE=60
REDIS_HOST=localhost
REDIS_PORT=6379

# CORS origins (comma-separated)
CORS_ORIGINS=https://golligog.com,https://www.golligog.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/golligog/proxy.log
```

#### Production WSGI Configuration
```python
# wsgi.py
from searxng_proxy import app
import os

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001))
    )
```

This backend development guide provides comprehensive coverage of both the Node.js authentication server and Python search proxy, including implementation details, security considerations, and testing strategies.
