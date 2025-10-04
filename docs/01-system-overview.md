# System Overview

## Architecture Components

The Golligog Search Engine is built as a modern, distributed system with clear separation of concerns across multiple layers.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Mobile    │ │     Web     │ │   Desktop   │ │   CLI  ││
│  │    Apps     │ │    Apps     │ │    Apps     │ │  Tools ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                  Gateway Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │     ALB     │ │ CloudFront  │ │   Route53   │ │   WAF  ││
│  │Load Balancer│ │     CDN     │ │     DNS     │ │Firewall││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                 Application Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   Node.js   │ │   Flask     │ │   Flutter   │ │  Auth  ││
│  │    API      │ │   Proxy     │ │    Web      │ │Service ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                   Service Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │   SearXNG   │ │   Redis     │ │  Elasticsearch│ │Monitoring││
│  │   Engine    │ │   Cache     │ │    Search     │ │ Stack ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐│
│  │ PostgreSQL  │ │     S3      │ │  CloudWatch │ │Secrets ││
│  │  Database   │ │   Storage   │ │    Logs     │ │Manager ││
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Frontend Applications

#### Flutter Mobile & Desktop Apps
- **Cross-platform**: Single codebase for Android, iOS, Windows, macOS, Linux
- **Material Design 3**: Dark theme with purple accent colors
- **Responsive UI**: Adaptive layouts for different screen sizes
- **Offline Support**: Cached search history and preferences
- **Performance**: Optimized builds for each platform

**Key Features:**
- User authentication with JWT tokens
- Real-time search with autocomplete
- Search history management
- Profile management
- Settings and preferences

#### Web Application
- **Progressive Web App**: Installable, offline-capable
- **Same Flutter Codebase**: Compiled to web with full feature parity
- **SEO Optimized**: Server-side rendering for search results
- **Fast Loading**: Code splitting and lazy loading

### 2. Backend Services

#### Node.js Authentication Server
```
Port: 5000
Framework: Express.js
Database: PostgreSQL via Prisma ORM
Authentication: JWT with refresh tokens
```

**Responsibilities:**
- User registration and authentication
- JWT token management
- User profile management
- Search history tracking
- Rate limiting and security

**API Endpoints:**
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/user/profile
PUT  /api/user/profile
GET  /api/user/history
POST /api/user/history
```

#### Flask Search Proxy
```
Port: 5001
Framework: Flask with CORS
Upstream: SearXNG Engine
Purpose: Source filtering and API transformation
```

**Responsibilities:**
- Proxy requests to SearXNG
- Filter out provider information
- Handle CORS for web clients
- Rate limiting and caching
- Response transformation

### 3. Search Engine (SearXNG)

#### Configuration
- **Google-only Results**: All other engines disabled
- **Privacy-focused**: No tracking, no logging
- **Source Filtering**: Provider names removed from results
- **Performance**: Cached results, optimized queries

**Enabled Engines:**
```yaml
engines:
  - google
  - google_images  
  - google_news
  - google_videos
  - google_scholar
```

**Search Categories:**
- General web search
- Image search
- News search
- Video search
- Academic search (Scholar)

### 4. Database Schema

#### PostgreSQL Tables
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Search history table
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    query TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    result_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User sessions table
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Data Flow Architecture

### Search Request Flow
```
1. User enters search query in Flutter app
2. App sends request to Flask proxy (/api/search)
3. Flask proxy forwards to SearXNG engine
4. SearXNG queries Google search engines
5. Results filtered and transformed by Flask proxy
6. Clean results returned to Flutter app
7. App displays results with dark theme UI
```

### Authentication Flow
```
1. User submits login credentials
2. Node.js server validates against PostgreSQL
3. JWT access token + refresh token generated
4. Tokens stored securely in app storage
5. Subsequent requests include Authorization header
6. Server validates JWT on each protected endpoint
7. Automatic token refresh when needed
```

## Technology Stack Details

### Frontend Technologies
```yaml
Flutter Framework:
  Version: 3.9+
  Language: Dart
  Platforms: Android, iOS, Web, Windows, macOS, Linux
  
Dependencies:
  - http: HTTP client for API calls
  - shared_preferences: Local storage
  - provider: State management
  - json_annotation: JSON serialization
  - url_launcher: External URL handling

Build Tools:
  - Flutter CLI
  - Dart build_runner
  - Platform-specific SDKs
```

### Backend Technologies
```yaml
Node.js Server:
  Runtime: Node.js 18+
  Framework: Express.js
  ORM: Prisma
  Database: PostgreSQL 15+
  Authentication: JWT + bcrypt

Flask Proxy:
  Runtime: Python 3.9+
  Framework: Flask
  Middleware: Flask-CORS
  HTTP Client: requests library

SearXNG Engine:
  Runtime: Python 3.9+
  Framework: Flask + Jinja2
  Search: Meta-search engine
  Configuration: YAML-based
```

### Infrastructure Technologies
```yaml
Cloud Platform: AWS
Compute: 
  - ECS Fargate for containers
  - EC2 for development
  - Lambda for serverless functions

Storage:
  - RDS PostgreSQL for database
  - S3 for static assets
  - ElastiCache for caching

Networking:
  - VPC with public/private subnets
  - Application Load Balancer
  - CloudFront CDN
  - Route 53 DNS

Security:
  - Certificate Manager for SSL
  - Secrets Manager for credentials
  - IAM for access control
  - WAF for application protection
```

## Performance Characteristics

### Search Performance
- **Average Response Time**: 500-800ms
- **P99 Response Time**: < 2 seconds
- **Concurrent Users**: 1000+ supported
- **Cache Hit Rate**: 70%+ for common queries
- **Uptime Target**: 99.9%

### Application Performance
```yaml
Flutter Mobile Apps:
  - APK Size: ~25MB (Android)
  - IPA Size: ~30MB (iOS)
  - Startup Time: < 2 seconds
  - Memory Usage: 50-100MB
  - Battery Impact: Minimal

Flutter Web App:
  - Initial Load: < 3 seconds
  - Bundle Size: ~2MB gzipped
  - First Contentful Paint: < 1.5s
  - Lighthouse Score: 90+

Backend Services:
  - Node.js API: < 100ms average
  - Flask Proxy: < 200ms average
  - Database Queries: < 50ms average
  - Memory Usage: < 512MB per service
```

## Security Architecture

### Data Protection
```yaml
Encryption:
  - TLS 1.3 for all communications
  - AES-256 for data at rest
  - JWT tokens with short expiry
  - Bcrypt for password hashing

Privacy:
  - No search query logging
  - Minimal user data collection
  - GDPR compliance
  - Cookie-free operation
```

### Network Security
```yaml
Infrastructure:
  - VPC with private subnets
  - Security groups for access control
  - WAF for application protection
  - DDoS protection via CloudFront

Application:
  - Rate limiting on all endpoints
  - Input validation and sanitization
  - CORS properly configured
  - Security headers implemented
```

## Scalability Design

### Horizontal Scaling
- **Stateless Services**: All backend services are stateless
- **Load Balancing**: Application Load Balancer distributes traffic
- **Auto Scaling**: ECS services scale based on CPU/memory
- **Database**: Read replicas for scaling reads

### Vertical Scaling
- **Resource Limits**: Configurable CPU/memory per service
- **Performance Monitoring**: CloudWatch metrics for optimization
- **Capacity Planning**: Usage-based scaling decisions

### Caching Strategy
```yaml
Application Level:
  - In-memory caching for frequent queries
  - Response caching in Flask proxy
  - Static asset caching via CloudFront

Database Level:
  - Connection pooling
  - Query result caching
  - Prepared statements for performance
```
