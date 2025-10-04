# Backend Technical Documentation
## Golligog Search Engine Backend Services

### Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Node.js Authentication Server](#nodejs-authentication-server)
4. [Python Search Proxy](#python-search-proxy)
5. [Database Design](#database-design)
6. [API Documentation](#api-documentation)
7. [Security Implementation](#security-implementation)
8. [Environment Configuration](#environment-configuration)
9. [Deployment Guide](#deployment-guide)
10. [Performance Optimization](#performance-optimization)
11. [Testing](#testing)
12. [Monitoring & Logging](#monitoring--logging)
13. [Troubleshooting](#troubleshooting)

---

## Overview

The Golligog backend consists of two complementary services that work together to provide authentication, user management, and search functionality:

1. **Node.js Authentication Server** (`/server/`) - Handles user management, authentication, and search history
2. **Python Search Proxy** (`/backend/`) - Proxies search requests to SearXNG with filtering and optimization

### Key Features
- **JWT-based Authentication**: Secure token-based authentication system
- **PostgreSQL Database**: Robust data persistence with Prisma ORM
- **Search Proxy**: Google-only search results with source filtering
- **Rate Limiting**: Protection against abuse and spam
- **Security Headers**: Helmet.js for security best practices
- **CORS Support**: Cross-origin resource sharing for Flutter frontend
- **Health Monitoring**: Built-in health check endpoints

### Technology Stack
```
Backend Services:
├── Node.js Authentication Server
│   ├── Express.js (Web Framework)
│   ├── Prisma (Database ORM)
│   ├── PostgreSQL (Database)
│   ├── JWT (Authentication)
│   ├── bcryptjs (Password Hashing)
│   └── Helmet.js (Security)
└── Python Search Proxy
    ├── Flask (Web Framework)
    ├── Requests (HTTP Client)
    ├── Flask-CORS (CORS Support)
    └── SearXNG Integration
```

---

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │───▶│  Node.js Server │───▶│   PostgreSQL    │
│                 │    │   (Port 5000)   │    │    Database     │
│  - Authentication│    │                 │    │                 │
│  - User Profile │    │  - JWT Auth     │    │  - Users        │
│  - Search UI    │    │  - User CRUD    │    │  - Search Hist. │
└─────────────────┘    │  - Rate Limiting│    └─────────────────┘
         │              └─────────────────┘              
         │                       │                       
         │              ┌─────────────────┐              │
         └─────────────▶│  Python Proxy   │───────────────┘
                        │   (Port 5001)   │
                        │                 │
                        │  - Search Proxy │    ┌─────────────────┐
                        │  - CORS Handler │───▶│     SearXNG     │
                        │  - Result Filter│    │   (Port 8080)   │
                        └─────────────────┘    └─────────────────┘
```

### Service Communication
- **Flutter ↔ Node.js**: Authentication, user management, search history
- **Flutter ↔ Python Proxy**: Search requests and results
- **Node.js ↔ PostgreSQL**: User data persistence
- **Python Proxy ↔ SearXNG**: Search query proxying and result filtering

---

## Node.js Authentication Server

### Project Structure
```
server/
├── server.js                 # Main server file
├── package.json              # Dependencies and scripts
├── .env                      # Environment variables
├── .env.example              # Environment template
├── prisma/
│   └── schema.prisma         # Database schema
├── config/
│   └── database.js           # Database configuration
├── middleware/
│   ├── auth.js               # Authentication middleware
│   └── validation.js         # Input validation
├── routes/
│   ├── auth.js               # Authentication routes
│   └── user.js               # User management routes
└── models/
    └── User.js               # User model (Prisma)
```

### Core Dependencies

```json
{
  "dependencies": {
    "@prisma/client": "^6.15.0",    // Database ORM client
    "bcryptjs": "^2.4.3",           // Password hashing
    "cors": "^2.8.5",               // CORS middleware
    "express": "^4.21.2",           // Web framework
    "express-rate-limit": "^6.11.2", // Rate limiting
    "helmet": "^7.2.0",             // Security headers
    "jsonwebtoken": "^9.0.2",       // JWT tokens
    "pg": "^8.16.3",                // PostgreSQL client
    "prisma": "^6.15.0"             // Database toolkit
  }
}
```

### Main Server Implementation

#### Server Initialization (`server.js`)

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { PrismaClient } = require('@prisma/client');

const app = express();
const prisma = new PrismaClient();

// Security middleware
app.use(helmet({
    crossOriginEmbedderPolicy: false,
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"]
        }
    }
}));

// CORS configuration
app.use(cors({
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: {
        error: 'Too many requests from this IP, please try again later.'
    },
    standardHeaders: true,
    legacyHeaders: false
});
app.use(limiter);
```

#### JWT Authentication Middleware

```javascript
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
        return res.status(401).json({ 
            message: 'Access token required',
            code: 'TOKEN_REQUIRED'
        });
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            if (err.name === 'TokenExpiredError') {
                return res.status(403).json({ 
                    message: 'Token has expired',
                    code: 'TOKEN_EXPIRED'
                });
            }
            return res.status(403).json({ 
                message: 'Invalid token',
                code: 'TOKEN_INVALID'
            });
        }
        req.user = user;
        next();
    });
};
```

### Authentication Endpoints

#### User Registration

```javascript
app.post('/api/auth/register', async (req, res) => {
    try {
        const { email, password, name } = req.body;

        // Validation
        if (!email || !password) {
            return res.status(400).json({ 
                message: 'Email and password are required',
                code: 'MISSING_FIELDS'
            });
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({ 
                message: 'Invalid email format',
                code: 'INVALID_EMAIL'
            });
        }

        // Password strength validation
        if (password.length < 8) {
            return res.status(400).json({ 
                message: 'Password must be at least 8 characters long',
                code: 'WEAK_PASSWORD'
            });
        }

        // Check if user already exists
        const existingUser = await prisma.user.findUnique({
            where: { email: email.toLowerCase() }
        });

        if (existingUser) {
            return res.status(409).json({ 
                message: 'User already exists with this email',
                code: 'USER_EXISTS'
            });
        }

        // Hash password
        const saltRounds = parseInt(process.env.BCRYPT_SALT_ROUNDS) || 12;
        const hashedPassword = await bcrypt.hash(password, saltRounds);

        // Create user
        const user = await prisma.user.create({
            data: {
                email: email.toLowerCase(),
                password: hashedPassword,
                name: name || null
            },
            select: {
                id: true,
                email: true,
                name: true,
                createdAt: true
            }
        });

        // Generate JWT token
        const token = jwt.sign(
            { 
                userId: user.id, 
                email: user.email 
            },
            process.env.JWT_SECRET,
            { 
                expiresIn: process.env.JWT_EXPIRE || '7d' 
            }
        );

        res.status(201).json({
            message: 'User registered successfully',
            user,
            token
        });

    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ 
            message: 'Internal server error during registration',
            code: 'REGISTRATION_ERROR'
        });
    }
});
```

#### User Login

```javascript
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // Validation
        if (!email || !password) {
            return res.status(400).json({ 
                message: 'Email and password are required',
                code: 'MISSING_CREDENTIALS'
            });
        }

        // Find user
        const user = await prisma.user.findUnique({
            where: { email: email.toLowerCase() }
        });

        if (!user) {
            return res.status(401).json({ 
                message: 'Invalid email or password',
                code: 'INVALID_CREDENTIALS'
            });
        }

        // Verify password
        const isValidPassword = await bcrypt.compare(password, user.password);
        if (!isValidPassword) {
            return res.status(401).json({ 
                message: 'Invalid email or password',
                code: 'INVALID_CREDENTIALS'
            });
        }

        // Generate JWT token
        const token = jwt.sign(
            { 
                userId: user.id, 
                email: user.email 
            },
            process.env.JWT_SECRET,
            { 
                expiresIn: process.env.JWT_EXPIRE || '7d' 
            }
        );

        // Return user data (exclude password)
        const { password: _, ...userWithoutPassword } = user;

        res.json({
            message: 'Login successful',
            user: userWithoutPassword,
            token
        });

    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ 
            message: 'Internal server error during login',
            code: 'LOGIN_ERROR'
        });
    }
});
```

### User Management Endpoints

#### Get User Profile

```javascript
app.get('/api/user/profile', authenticateToken, async (req, res) => {
    try {
        const user = await prisma.user.findUnique({
            where: { id: req.user.userId },
            select: {
                id: true,
                email: true,
                name: true,
                createdAt: true,
                updatedAt: true,
                _count: {
                    select: {
                        searchHistory: true
                    }
                }
            }
        });

        if (!user) {
            return res.status(404).json({ 
                message: 'User not found',
                code: 'USER_NOT_FOUND'
            });
        }

        res.json({
            message: 'Profile retrieved successfully',
            user
        });

    } catch (error) {
        console.error('Profile retrieval error:', error);
        res.status(500).json({ 
            message: 'Internal server error',
            code: 'PROFILE_ERROR'
        });
    }
});
```

#### Update User Profile

```javascript
app.put('/api/user/profile', authenticateToken, async (req, res) => {
    try {
        const { name } = req.body;
        
        const updatedUser = await prisma.user.update({
            where: { id: req.user.userId },
            data: { name },
            select: {
                id: true,
                email: true,
                name: true,
                updatedAt: true
            }
        });

        res.json({
            message: 'Profile updated successfully',
            user: updatedUser
        });

    } catch (error) {
        console.error('Profile update error:', error);
        res.status(500).json({ 
            message: 'Internal server error',
            code: 'UPDATE_ERROR'
        });
    }
});
```

### Search History Management

#### Save Search Query

```javascript
app.post('/api/user/search-history', authenticateToken, async (req, res) => {
    try {
        const { query } = req.body;

        if (!query || query.trim().length === 0) {
            return res.status(400).json({ 
                message: 'Search query is required',
                code: 'MISSING_QUERY'
            });
        }

        const searchEntry = await prisma.searchHistory.create({
            data: {
                query: query.trim(),
                userId: req.user.userId
            }
        });

        res.status(201).json({
            message: 'Search query saved',
            searchEntry
        });

    } catch (error) {
        console.error('Search history save error:', error);
        res.status(500).json({ 
            message: 'Failed to save search query',
            code: 'SAVE_ERROR'
        });
    }
});
```

#### Get Search History

```javascript
app.get('/api/user/search-history', authenticateToken, async (req, res) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 20;
        const offset = (page - 1) * limit;

        const [searchHistory, totalCount] = await Promise.all([
            prisma.searchHistory.findMany({
                where: { userId: req.user.userId },
                orderBy: { createdAt: 'desc' },
                take: limit,
                skip: offset
            }),
            prisma.searchHistory.count({
                where: { userId: req.user.userId }
            })
        ]);

        res.json({
            message: 'Search history retrieved',
            searchHistory,
            pagination: {
                page,
                limit,
                total: totalCount,
                totalPages: Math.ceil(totalCount / limit)
            }
        });

    } catch (error) {
        console.error('Search history retrieval error:', error);
        res.status(500).json({ 
            message: 'Failed to retrieve search history',
            code: 'RETRIEVAL_ERROR'
        });
    }
});
```

---

## Python Search Proxy

### Project Structure
```
backend/
├── searxng_proxy.py          # Main Flask application
├── requirements.txt          # Python dependencies
└── config.py                 # Configuration settings
```

### Dependencies (`requirements.txt`)

```text
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
```

### Core Implementation

#### Flask Application Setup

```python
#!/usr/bin/env python3
"""
SearXNG Proxy Server for Golligog Search Engine
Provides Google-only search results with source filtering
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import time
from datetime import datetime

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:5000',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5000'
])

# Configuration
SEARXNG_BASE_URL = os.environ.get('SEARXNG_URL', 'http://localhost:8080')
SEARXNG_SEARCH_ENDPOINT = '/search'
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))
MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))

# Public SearXNG instances as fallback
PUBLIC_INSTANCES = [
    'https://search.sapti.me',
    'https://searx.be',
    'https://searx.info',
    'https://search.mdosch.de',
    'https://searx.tiekoetter.com'
]
```

#### Search Instance Management

```python
def search_with_instance(instance_url, params, timeout=REQUEST_TIMEOUT):
    """
    Search using a specific SearXNG instance with error handling
    """
    try:
        headers = {
            'User-Agent': 'Golligog-Search-Engine/1.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'DNT': '1',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get(
            f"{instance_url}{SEARXNG_SEARCH_ENDPOINT}",
            params=params,
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )
        
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print(f"Invalid JSON response from {instance_url}")
                return None
        else:
            print(f"HTTP {response.status_code} from {instance_url}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"Timeout error with instance {instance_url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Connection error with instance {instance_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error with instance {instance_url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error with instance {instance_url}: {e}")
        return None
```

#### Result Filtering System

```python
def filter_result_sources(result_data):
    """
    Remove source information and clean up search results
    """
    if not result_data or 'results' not in result_data:
        return result_data
    
    filtered_results = []
    
    for result in result_data['results']:
        # Create clean result without provider information
        clean_result = {
            'title': result.get('title', '').strip(),
            'url': result.get('url', '').strip(),
            'content': result.get('content', '').strip(),
            'publishedDate': result.get('publishedDate'),
            'thumbnail': result.get('thumbnail'),
            'template': result.get('template', 'default')
        }
        
        # Remove empty fields
        clean_result = {k: v for k, v in clean_result.items() 
                      if v is not None and v != ''}
        
        # Only include results with minimum required fields
        if clean_result.get('title') and clean_result.get('url'):
            filtered_results.append(clean_result)
    
    # Update result data
    result_data['results'] = filtered_results
    result_data['number_of_results'] = len(filtered_results)
    
    # Remove metadata that reveals sources
    metadata_to_remove = [
        'engines', 'unresponsive_engines', 'engine_data',
        'answers', 'infoboxes', 'suggestions'
    ]
    
    for key in metadata_to_remove:
        if key in result_data:
            del result_data[key]
    
    return result_data
```

#### Google Engine Mapping

```python
def get_google_engine_for_category(category):
    """
    Map search categories to specific Google engines
    """
    google_engines_map = {
        'general': 'google',
        'web': 'google',
        'images': 'google_images',
        'news': 'google_news',
        'videos': 'google_videos',
        'science': 'google_scholar',
        'scholar': 'google_scholar',
        'files': 'google_scholar',
        'academic': 'google_scholar',
        'map': 'google',
        'maps': 'google'
    }
    
    return google_engines_map.get(category.lower(), 'google')
```

#### Main Search Endpoint

```python
@app.route('/api/search', methods=['GET'])
def search():
    """
    Main search endpoint with Google-only results and source filtering
    """
    start_time = time.time()
    
    # Extract and validate parameters
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({
            'error': 'Query parameter "q" is required',
            'code': 'MISSING_QUERY'
        }), 400
    
    if len(query) > 500:
        return jsonify({
            'error': 'Query too long (max 500 characters)',
            'code': 'QUERY_TOO_LONG'
        }), 400
    
    # Get search parameters
    category = request.args.get('category', 'general')
    page = request.args.get('page', '1')
    lang = request.args.get('lang', 'en')
    
    # Force Google engine based on category
    selected_engine = get_google_engine_for_category(category)
    
    # Build search parameters
    search_params = {
        'q': query,
        'format': 'json',
        'engines': selected_engine,
        'language': lang,
        'pageno': page,
        'time_range': '',
        'safesearch': '0'
    }
    
    # Try local instance first
    result = None
    instances_tried = []
    
    # Primary: Local SearXNG instance
    if SEARXNG_BASE_URL:
        instances_tried.append(SEARXNG_BASE_URL)
        result = search_with_instance(SEARXNG_BASE_URL, search_params)
    
    # Fallback: Public SearXNG instances
    if not result:
        for instance in PUBLIC_INSTANCES:
            instances_tried.append(instance)
            result = search_with_instance(instance, search_params)
            if result:
                break
    
    # Process results
    if result:
        # Filter out source information
        filtered_result = filter_result_sources(result)
        
        # Add metadata
        filtered_result['query'] = query
        filtered_result['category'] = category
        filtered_result['search_time'] = round(time.time() - start_time, 3)
        filtered_result['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        return jsonify(filtered_result)
    else:
        return jsonify({
            'error': 'All search instances are unavailable',
            'code': 'NO_INSTANCES_AVAILABLE',
            'query': query,
            'instances_tried': instances_tried,
            'number_of_results': 0,
            'results': []
        }), 503
```

#### Health Check and Monitoring

```python
@app.route('/api/health', methods=['GET'])
def health():
    """
    Comprehensive health check endpoint
    """
    health_data = {
        'status': 'unknown',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'local_instance': {
            'url': SEARXNG_BASE_URL,
            'status': 'unknown',
            'response_time': None
        },
        'public_instances': [],
        'system': {
            'python_version': os.sys.version,
            'flask_version': Flask.__version__
        }
    }
    
    overall_healthy = False
    
    # Check local instance
    if SEARXNG_BASE_URL:
        start_time = time.time()
        try:
            response = requests.get(
                f"{SEARXNG_BASE_URL}/",
                timeout=5,
                headers={'User-Agent': 'Golligog-Health-Check/1.0'}
            )
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                health_data['local_instance']['status'] = 'healthy'
                health_data['local_instance']['response_time'] = f"{response_time}ms"
                overall_healthy = True
            else:
                health_data['local_instance']['status'] = f'unhealthy (HTTP {response.status_code})'
                
        except Exception as e:
            health_data['local_instance']['status'] = f'unhealthy ({str(e)})'
    
    # Check first 3 public instances
    for instance in PUBLIC_INSTANCES[:3]:
        instance_health = {
            'url': instance,
            'status': 'unknown',
            'response_time': None
        }
        
        start_time = time.time()
        try:
            response = requests.get(f"{instance}/", timeout=3)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                instance_health['status'] = 'healthy'
                instance_health['response_time'] = f"{response_time}ms"
                overall_healthy = True
            else:
                instance_health['status'] = f'unhealthy (HTTP {response.status_code})'
                
        except Exception as e:
            instance_health['status'] = f'unhealthy ({str(e)})'
        
        health_data['public_instances'].append(instance_health)
    
    health_data['status'] = 'healthy' if overall_healthy else 'unhealthy'
    
    status_code = 200 if overall_healthy else 503
    return jsonify(health_data), status_code
```

---

## Database Design

### Prisma Schema (`prisma/schema.prisma`)

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  name      String?
  isActive  Boolean  @default(true)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  lastLogin DateTime?
  
  // Relationships
  searchHistory SearchHistory[]
  userSettings  UserSettings?
  
  @@map("users")
  @@index([email])
  @@index([createdAt])
}

model SearchHistory {
  id        String   @id @default(cuid())
  query     String
  category  String   @default("general")
  userId    String
  metadata  Json?    // Store additional search metadata
  createdAt DateTime @default(now())
  
  // Relationships
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("search_history")
  @@index([userId, createdAt])
  @@index([createdAt])
}

model UserSettings {
  id               String  @id @default(cuid())
  userId           String  @unique
  theme            String  @default("dark")
  language         String  @default("en")
  safeSearch       Boolean @default(false)
  resultsPerPage   Int     @default(10)
  autoSaveHistory  Boolean @default(true)
  
  // Relationships
  user             User    @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("user_settings")
}
```

### Database Migrations

#### Initial Migration

```sql
-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "lastLogin" TIMESTAMP(3),

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "search_history" (
    "id" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "category" TEXT NOT NULL DEFAULT 'general',
    "userId" TEXT NOT NULL,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "search_history_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_settings" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "theme" TEXT NOT NULL DEFAULT 'dark',
    "language" TEXT NOT NULL DEFAULT 'en',
    "safeSearch" BOOLEAN NOT NULL DEFAULT false,
    "resultsPerPage" INTEGER NOT NULL DEFAULT 10,
    "autoSaveHistory" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "user_settings_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");
CREATE INDEX "users_email_idx" ON "users"("email");
CREATE INDEX "users_createdAt_idx" ON "users"("createdAt");

-- CreateIndex
CREATE INDEX "search_history_userId_createdAt_idx" ON "search_history"("userId", "createdAt");
CREATE INDEX "search_history_createdAt_idx" ON "search_history"("createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "user_settings_userId_key" ON "user_settings"("userId");

-- AddForeignKey
ALTER TABLE "search_history" ADD CONSTRAINT "search_history_userId_fkey" 
    FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "user_settings" ADD CONSTRAINT "user_settings_userId_fkey" 
    FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
```

---

## API Documentation

### Authentication Endpoints

#### POST `/api/auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2024-01-01T00:00:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### User Management Endpoints

#### GET `/api/user/profile`
Get authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Profile retrieved successfully",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "_count": {
      "searchHistory": 42
    }
  }
}
```

### Search Endpoints

#### GET `/api/search`
Perform search with Google-only results.

**Query Parameters:**
- `q` (required): Search query
- `category` (optional): Search category (general, images, news, videos, science)
- `page` (optional): Page number (default: 1)
- `lang` (optional): Language code (default: en)

**Example Request:**
```
GET /api/search?q=flutter%20development&category=general&page=1
```

**Response (200):**
```json
{
  "query": "flutter development",
  "category": "general",
  "number_of_results": 15,
  "search_time": 0.843,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "results": [
    {
      "title": "Flutter - Build apps for any screen",
      "url": "https://flutter.dev/",
      "content": "Flutter is Google's UI toolkit for building...",
      "thumbnail": "https://flutter.dev/images/flutter-logo.png"
    }
  ]
}
```

### Health Check Endpoints

#### GET `/health` (Node.js Server)
Check Node.js server and database health.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

#### GET `/api/health` (Python Proxy)
Check search proxy and SearXNG instances health.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "local_instance": {
    "url": "http://localhost:8080",
    "status": "healthy",
    "response_time": "156ms"
  },
  "public_instances": [
    {
      "url": "https://search.sapti.me",
      "status": "healthy",
      "response_time": "234ms"
    }
  ]
}
```

---

## Security Implementation

### Authentication Security

#### JWT Token Management
```javascript
// Token generation with expiration
const generateToken = (user) => {
    return jwt.sign(
        { 
            userId: user.id, 
            email: user.email,
            iat: Math.floor(Date.now() / 1000),
            iss: 'golligog-backend'
        },
        process.env.JWT_SECRET,
        { 
            expiresIn: '7d',
            algorithm: 'HS256'
        }
    );
};

// Token refresh mechanism
app.post('/api/auth/refresh', authenticateToken, async (req, res) => {
    try {
        const user = await prisma.user.findUnique({
            where: { id: req.user.userId },
            select: { id: true, email: true, isActive: true }
        });

        if (!user || !user.isActive) {
            return res.status(401).json({ 
                message: 'User account is inactive',
                code: 'ACCOUNT_INACTIVE'
            });
        }

        const newToken = generateToken(user);
        
        res.json({
            message: 'Token refreshed successfully',
            token: newToken
        });
    } catch (error) {
        res.status(500).json({ 
            message: 'Token refresh failed',
            code: 'REFRESH_ERROR'
        });
    }
});
```

#### Password Security
```javascript
const bcrypt = require('bcryptjs');

// Strong password hashing
const hashPassword = async (password) => {
    const saltRounds = 12; // High computational cost
    return await bcrypt.hash(password, saltRounds);
};

// Password strength validation
const validatePasswordStrength = (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    
    const errors = [];
    
    if (password.length < minLength) {
        errors.push(`Password must be at least ${minLength} characters long`);
    }
    if (!hasUpperCase) {
        errors.push('Password must contain at least one uppercase letter');
    }
    if (!hasLowerCase) {
        errors.push('Password must contain at least one lowercase letter');
    }
    if (!hasNumbers) {
        errors.push('Password must contain at least one number');
    }
    if (!hasSpecialChar) {
        errors.push('Password must contain at least one special character');
    }
    
    return {
        isValid: errors.length === 0,
        errors
    };
};
```

### Rate Limiting and DDoS Protection

```javascript
const rateLimit = require('express-rate-limit');

// Different rate limits for different endpoints
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Limit auth attempts
    message: {
        error: 'Too many authentication attempts, please try again later.',
        code: 'RATE_LIMIT_AUTH'
    },
    standardHeaders: true,
    legacyHeaders: false,
    skip: (req, res) => {
        // Skip rate limiting for successful requests
        return res.statusCode < 400;
    }
});

const searchLimiter = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 60, // 60 searches per minute
    message: {
        error: 'Too many search requests, please slow down.',
        code: 'RATE_LIMIT_SEARCH'
    }
});

// Apply rate limiters
app.use('/api/auth', authLimiter);
app.use('/api/search', searchLimiter);
```

### Input Validation and Sanitization

```javascript
const { body, query, validationResult } = require('express-validator');

// Input validation middleware
const validateRegistration = [
    body('email')
        .isEmail()
        .normalizeEmail()
        .withMessage('Valid email is required'),
    body('password')
        .isLength({ min: 8 })
        .withMessage('Password must be at least 8 characters')
        .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
        .withMessage('Password must contain uppercase, lowercase, number and special character'),
    body('name')
        .optional()
        .isLength({ min: 2, max: 50 })
        .withMessage('Name must be between 2 and 50 characters')
        .escape()
];

const validateSearch = [
    query('q')
        .isLength({ min: 1, max: 500 })
        .withMessage('Query must be between 1 and 500 characters')
        .escape(),
    query('category')
        .optional()
        .isIn(['general', 'images', 'news', 'videos', 'science'])
        .withMessage('Invalid category'),
    query('page')
        .optional()
        .isInt({ min: 1, max: 100 })
        .withMessage('Page must be between 1 and 100')
];

// Validation error handler
const handleValidationErrors = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({
            message: 'Validation failed',
            errors: errors.array(),
            code: 'VALIDATION_ERROR'
        });
    }
    next();
};
```

### CORS and Security Headers

```javascript
const helmet = require('helmet');
const cors = require('cors');

// Security headers
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            scriptSrc: ["'self'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "https://api.golligog.com"],
            fontSrc: ["'self'", "https://fonts.googleapis.com"],
            objectSrc: ["'none'"],
            upgradeInsecureRequests: []
        }
    },
    crossOriginEmbedderPolicy: false,
    crossOriginResourcePolicy: { policy: "cross-origin" }
}));

// CORS configuration
const corsOptions = {
    origin: function (origin, callback) {
        const allowedOrigins = [
            'http://localhost:3000',
            'http://localhost:3001',
            'https://golligog.com',
            'https://www.golligog.com'
        ];
        
        if (!origin || allowedOrigins.indexOf(origin) !== -1) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    },
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    exposedHeaders: ['X-Total-Count'],
    maxAge: 86400 // Cache preflight response for 24 hours
};

app.use(cors(corsOptions));
```

---

## Environment Configuration

### Node.js Server Environment (`.env`)

```bash
# Application Configuration
NODE_ENV=production
PORT=5000
APP_NAME=Golligog Backend
APP_VERSION=1.0.0

# Database Configuration
DATABASE_URL="postgresql://username:password@localhost:5432/golligog_db?schema=public"
DB_POOL_MIN=2
DB_POOL_MAX=10
DB_IDLE_TIMEOUT=30000
DB_CONNECTION_TIMEOUT=60000

# JWT Configuration
JWT_SECRET=your_super_secure_jwt_secret_key_here_minimum_32_characters_long
JWT_EXPIRE=7d
JWT_REFRESH_EXPIRE=30d

# Security Configuration
BCRYPT_SALT_ROUNDS=12
SESSION_SECRET=your_session_secret_here

# CORS Configuration
CORS_ORIGIN=http://localhost:3000,https://golligog.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_AUTH_MAX=5
RATE_LIMIT_SEARCH_MAX=60

# Logging
LOG_LEVEL=info
LOG_FILE_PATH=./logs/app.log
LOG_MAX_SIZE=10m
LOG_MAX_FILES=5

# External Services
SEARXNG_URL=http://localhost:8080
EMAIL_SERVICE_URL=https://api.sendgrid.com
EMAIL_FROM=noreply@golligog.com

# Monitoring
HEALTH_CHECK_INTERVAL=30000
METRICS_ENABLED=true
PROMETHEUS_PORT=9090
```

### Python Proxy Environment

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_SECRET_KEY=your_flask_secret_key_here

# SearXNG Configuration
SEARXNG_URL=http://localhost:8080
REQUEST_TIMEOUT=10
MAX_RETRIES=3
CACHE_TIMEOUT=300

# Search Configuration
DEFAULT_LANGUAGE=en
DEFAULT_SAFE_SEARCH=0
RESULTS_PER_PAGE=10
MAX_QUERY_LENGTH=500

# Public Instance Rotation
USE_PUBLIC_INSTANCES=true
INSTANCE_ROTATION_ENABLED=true
INSTANCE_HEALTH_CHECK_INTERVAL=60

# Performance
WORKER_PROCESSES=4
WORKER_CONNECTIONS=1000
KEEP_ALIVE=65

# Security
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
IP_WHITELIST=
IP_BLACKLIST=

# Monitoring
HEALTH_CHECK_ENABLED=true
METRICS_ENDPOINT_ENABLED=true
LOG_SEARCH_QUERIES=false
```

---

## Deployment Guide

### Development Environment

#### Prerequisites
```bash
# Install Node.js (v16+)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python (v3.9+)
sudo apt-get update
sudo apt-get install python3.9 python3.9-pip python3.9-venv

# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Install Docker (for SearXNG)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Setup Steps

1. **Database Setup**
```bash
# Create database user and database
sudo -u postgres psql
CREATE USER golligog_user WITH PASSWORD 'secure_password';
CREATE DATABASE golligog_db OWNER golligog_user;
GRANT ALL PRIVILEGES ON DATABASE golligog_db TO golligog_user;
\q
```

2. **Node.js Server Setup**
```bash
cd server
npm install
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
npx prisma migrate dev
npx prisma generate

# Start development server
npm run dev
```

3. **Python Proxy Setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start proxy server
python3 searxng_proxy.py
```

### Production Deployment

#### Docker Containerization

**Node.js Dockerfile** (`server/Dockerfile`)
```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

CMD ["node", "server.js"]
```

**Python Proxy Dockerfile** (`backend/Dockerfile`)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/api/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "searxng_proxy:app"]
```

#### Docker Compose Configuration

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: golligog_db
      POSTGRES_USER: golligog_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U golligog_user -d golligog_db"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  searxng:
    image: searxng/searxng:latest
    volumes:
      - ./searxng/settings.yml:/etc/searxng/settings.yml
    ports:
      - "8080:8080"
    environment:
      SEARXNG_SECRET: ${SEARXNG_SECRET}
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/healthz"]
      interval: 30s
      timeout: 10s
      retries: 5

  backend:
    build: ./server
    environment:
      NODE_ENV: production
      DATABASE_URL: postgresql://golligog_user:${DB_PASSWORD}@postgres:5432/golligog_db
      JWT_SECRET: ${JWT_SECRET}
      CORS_ORIGIN: ${CORS_ORIGIN}
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  search-proxy:
    build: ./backend
    environment:
      SEARXNG_URL: http://searxng:8080
      FLASK_ENV: production
    ports:
      - "5001:5001"
    depends_on:
      searxng:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - search-proxy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  postgres_data:
  redis_data:
```

#### Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:5000;
    }
    
    upstream search_proxy {
        server search-proxy:5001;
    }
    
    upstream searxng {
        server searxng:8080;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=search:10m rate=60r/m;
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;

    server {
        listen 80;
        server_name api.golligog.com;
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
        
        # Auth endpoints (with stricter rate limiting)
        location /api/auth/ {
            limit_req zone=auth burst=3 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Search endpoints
        location /api/search {
            limit_req zone=search burst=10 nodelay;
            proxy_pass http://search_proxy;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API endpoints
        location /api/ {
            limit_req zone=general burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health checks (no rate limiting)
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
        
        # SearXNG direct access (internal only)
        location /searxng/ {
            internal;
            proxy_pass http://searxng/;
        }
    }
}
```

---

## Performance Optimization

### Database Optimization

#### Connection Pooling
```javascript
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
  previewFeatures = ["clientExtensions"]
}

// Connection pooling configuration
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL
    }
  },
  log: ['error', 'warn'],
  errorFormat: 'pretty'
});
```

#### Query Optimization
```sql
-- Indexes for better performance
CREATE INDEX CONCURRENTLY idx_users_email_active ON users(email) WHERE "isActive" = true;
CREATE INDEX CONCURRENTLY idx_search_history_user_date ON search_history(userId, createdAt DESC);
CREATE INDEX CONCURRENTLY idx_search_history_query ON search_history USING gin(to_tsvector('english', query));

-- Partitioning for large search history tables
CREATE TABLE search_history_2024 PARTITION OF search_history
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Query optimization with prepared statements
PREPARE get_user_history (text, int, int) AS
SELECT id, query, category, createdAt 
FROM search_history 
WHERE userId = $1 
ORDER BY createdAt DESC 
LIMIT $2 OFFSET $3;
```

### Caching Strategy

#### Redis Integration
```javascript
const redis = require('redis');
const client = redis.createClient({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    retry_delay: 1000,
    max_attempts: 3
});

// Cache middleware
const cacheMiddleware = (duration = 300) => {
    return async (req, res, next) => {
        const key = `cache:${req.originalUrl}`;
        
        try {
            const cached = await client.get(key);
            if (cached) {
                return res.json(JSON.parse(cached));
            }
            
            // Store original res.json
            const originalJson = res.json;
            res.json = function(data) {
                // Cache the response
                client.setEx(key, duration, JSON.stringify(data));
                return originalJson.call(this, data);
            };
            
            next();
        } catch (error) {
            console.error('Cache error:', error);
            next();
        }
    };
};

// Apply caching to search endpoints
app.get('/api/search', cacheMiddleware(300), search);
```

#### Application-Level Caching
```python
# Python proxy caching
from functools import lru_cache
import time
from typing import Dict, Any, Optional

class SearchCache:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        # Implement LRU eviction if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

# Global cache instance
search_cache = SearchCache(max_size=500, ttl=300)

@app.route('/api/search', methods=['GET'])
def search():
    # Create cache key from parameters
    cache_key = f"search:{query}:{category}:{page}"
    
    # Check cache first
    cached_result = search_cache.get(cache_key)
    if cached_result:
        return jsonify(cached_result)
    
    # Perform search and cache result
    result = perform_search(query, category, page)
    if result:
        search_cache.set(cache_key, result)
    
    return jsonify(result)
```

### Monitoring and Metrics

#### Prometheus Integration
```javascript
const prometheus = require('prom-client');

// Create metrics
const httpRequestDuration = new prometheus.Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new prometheus.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
});

const searchRequestsTotal = new prometheus.Counter({
    name: 'search_requests_total',
    help: 'Total number of search requests',
    labelNames: ['category', 'status']
});

// Middleware to collect metrics
app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;
        const route = req.route ? req.route.path : req.path;
        
        httpRequestDuration
            .labels(req.method, route, res.statusCode)
            .observe(duration);
        
        httpRequestTotal
            .labels(req.method, route, res.statusCode)
            .inc();
    });
    
    next();
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
    res.set('Content-Type', prometheus.register.contentType);
    res.send(prometheus.register.metrics());
});
```

---

This comprehensive backend documentation covers all aspects of the Golligog search engine backend implementation, from architecture and security to deployment and monitoring. The documentation provides detailed code examples, configuration files, and best practices for maintaining and scaling the backend services.
