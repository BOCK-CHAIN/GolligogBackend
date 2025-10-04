# SearXNG Configuration

## Overview

SearXNG is a privacy-focused meta-search engine that aggregates results from multiple search engines without storing user data. For Golligog, it's configured to provide Google-only results while maintaining privacy and filtering out source information.

## Installation & Setup

### Prerequisites
```bash
# System requirements
- Python 3.9+
- Redis (optional, for caching)
- Git
- virtualenv or Docker
```

### Local Development Setup

#### Method 1: Direct Installation
```bash
# Clone SearXNG
git clone https://github.com/searxng/searxng.git
cd searxng

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -U pip setuptools wheel pyyaml
pip install -e .

# Set environment variables
export SEARXNG_SETTINGS_PATH="${PWD}/searx/settings.yml"

# Run development server
python searx/webapp.py
```

#### Method 2: Docker Setup
```bash
# Clone and build
git clone https://github.com/searxng/searxng.git
cd searxng

# Build Docker image
docker build -t searxng .

# Run container
docker run -d \
  --name searxng \
  -p 8080:8080 \
  -v "$(pwd)/searx/settings.yml:/etc/searx/settings.yml" \
  searxng
```

### Production Setup

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.7'

services:
  searxng:
    build: .
    container_name: searxng
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./searx/settings.yml:/etc/searx/settings.yml:ro
      - searxng-data:/var/log/uwsgi
    environment:
      - SEARXNG_BASE_URL=https://search.golligog.com/
      - SEARXNG_SECRET_KEY=${SEARXNG_SECRET_KEY}
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    container_name: searxng-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

volumes:
  searxng-data:
  redis-data:
```

## Google-Only Configuration

### Engine Configuration

#### Primary Google Engines
```yaml
# searx/settings.yml
engines:
  # Web Search
  - name: google
    engine: google
    shortcut: go
    use_mobile_ui: false
    disabled: false
    
  # Image Search  
  - name: google images
    engine: google_images
    shortcut: goi
    disabled: false
    
  # News Search
  - name: google news
    engine: google_news
    shortcut: gon
    disabled: false
    
  # Video Search
  - name: google videos
    engine: google_videos
    shortcut: gov
    disabled: false
    
  # Academic Search
  - name: google scholar
    engine: google_scholar
    shortcut: gos
    disabled: false
```

#### Disabled Engines
```yaml
# All other engines disabled for Google-only results
engines:
  - name: bing
    engine: bing
    disabled: true
    
  - name: duckduckgo
    engine: duckduckgo
    disabled: true
    
  - name: yahoo
    engine: yahoo
    disabled: true
    
  # ... 200+ other engines disabled
```

### Automated Configuration Script

#### Google-Only Setup Script
```python
#!/usr/bin/env python3
# configure_google_only.py

import yaml
import os
from pathlib import Path

def configure_google_only():
    """Configure SearXNG for Google-only search results"""
    
    settings_path = Path(__file__).parent / 'searxng' / 'searx' / 'settings.yml'
    
    if not settings_path.exists():
        print(f"Settings file not found: {settings_path}")
        return False
    
    # Read current settings
    with open(settings_path, 'r') as f:
        settings = yaml.safe_load(f)
    
    # Google engines to keep enabled
    google_engines = {
        'google',
        'google images', 
        'google news',
        'google videos',
        'google scholar'
    }
    
    # Configure engines
    engines_modified = 0
    for engine in settings.get('engines', []):
        engine_name = engine.get('name', '')
        
        if engine_name in google_engines:
            if engine.get('disabled', False):
                engine['disabled'] = False
                engines_modified += 1
                print(f"✓ Enabled: {engine_name}")
        else:
            if not engine.get('disabled', False):
                engine['disabled'] = True
                engines_modified += 1
                print(f"✗ Disabled: {engine_name}")
    
    # Update general settings
    if 'general' not in settings:
        settings['general'] = {}
    
    settings['general'].update({
        'instance_name': 'Golligog Search',
        'contact_url': False,
        'enable_metrics': False,
        'debug': False
    })
    
    # Update search settings
    if 'search' not in settings:
        settings['search'] = {}
        
    settings['search'].update({
        'safe_search': 0,
        'autocomplete': '',
        'favicon_resolver': '',
        'default_lang': 'auto'
    })
    
    # Update UI settings
    if 'ui' not in settings:
        settings['ui'] = {}
        
    settings['ui'].update({
        'static_use_hash': True,
        'default_theme': 'dark',
        'center_alignment': True,
        'results_on_new_tab': False,
        'hotkeys': 'default'
    })
    
    # Write updated settings
    with open(settings_path, 'w') as f:
        yaml.dump(settings, f, default_flow_style=False, indent=2)
    
    print(f"\n✓ Configuration completed!")
    print(f"✓ Modified {engines_modified} engines")
    print(f"✓ Enabled {len(google_engines)} Google engines")
    print(f"✓ Settings saved to: {settings_path}")
    
    return True

if __name__ == '__main__':
    configure_google_only()
```

### Advanced Configuration

#### Performance Settings
```yaml
# searx/settings.yml
general:
  # Performance
  default_http_headers:
    X-Content-Type-Options: nosniff
    X-XSS-Protection: 1; mode=block
    X-Download-Options: noopen
    X-Robots-Tag: noindex, nofollow
    Referrer-Policy: no-referrer
  
  # Request settings
  request_timeout: 10.0
  useragent_suffix: ""
  pool_connections: 100
  pool_maxsize: 20
  
search:
  # Results per page
  default_results: 10
  max_page: 10
  
  # Language and region
  languages:
    - en
    - en-US
  
  # Safe search (0=off, 1=moderate, 2=strict)
  safe_search: 0
  
  # Autocomplete disabled for privacy
  autocomplete: ""
  autocomplete_min: 4
```

#### Category Mapping
```yaml
categories_as_tabs:
  general:
    - google
  images:
    - google images
  news:
    - google news
  videos:
    - google videos
  science:
    - google scholar
```

#### Custom Outgoing Headers
```yaml
outgoing:
  request_timeout: 10.0
  useragent_suffix: "Golligog/1.0"
  pool_connections: 100
  pool_maxsize: 20
  
  # Custom headers to avoid blocking
  extra_proxy_timeout: 20.0
  headers:
    User-Agent: "Mozilla/5.0 (compatible; Golligog/1.0)"
    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    Accept-Language: "en-US,en;q=0.5"
    Accept-Encoding: "gzip, deflate"
    DNT: "1"
    Connection: "keep-alive"
    Upgrade-Insecure-Requests: "1"
```

## Privacy & Security Settings

### Privacy Configuration
```yaml
# No logging or tracking
general:
  debug: false
  enable_metrics: false
  logger: false
  
search:
  # No query logging
  query_in_title: false
  
server:
  # Secure headers
  secret_key: "${SEARXNG_SECRET_KEY}"
  limiter: true
  public_instance: false
  
  # Rate limiting
  default_rate_limit:
    GET: "100/hour"
    POST: "50/hour"
```

### Security Headers
```yaml
server:
  http_protocol_version: "1.1"
  method: "POST"
  
  # Security headers
  default_http_headers:
    X-Content-Type-Options: nosniff
    X-XSS-Protection: "1; mode=block"
    X-Download-Options: noopen
    X-Robots-Tag: "noindex, nofollow"
    Referrer-Policy: "no-referrer"
    X-Frame-Options: "DENY"
    Content-Security-Policy: "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;"
```

### Environment Variables
```bash
# .env file for SearXNG
SEARXNG_SECRET_KEY=your-super-secret-key-here
SEARXNG_BASE_URL=https://search.golligog.com/
SEARXNG_PORT=8080
SEARXNG_BIND_ADDRESS=0.0.0.0

# Redis caching (optional)
REDIS_URL=redis://localhost:6379/0

# Logging
SEARXNG_LOG_LEVEL=INFO
SEARXNG_LOG_FILE=/var/log/searxng/searxng.log
```

## Performance Optimization

### Caching Configuration
```yaml
# Redis caching setup
redis:
  url: redis://localhost:6379/0
  
# Result caching
caching:
  default_timeout: 300
  cache_type: redis
  
  # Cache keys
  key_prefix: "searxng:"
  
  # Memory usage
  threshold: 500
```

### Response Time Optimization
```yaml
# Engine timeouts
engines:
  - name: google
    timeout: 10.0
    
  - name: google images
    timeout: 15.0
    
  - name: google news
    timeout: 10.0
    
# Request pooling
outgoing:
  pool_connections: 100
  pool_maxsize: 20
  retries: 2
  
# Concurrent requests
search:
  max_request_timeout: 30.0
  concurrent_requests: 10
```

### Memory Management
```yaml
server:
  # Worker processes
  workers: 4
  
  # Memory limits  
  worker_memory_limit: 512
  
  # Connection limits
  worker_connections: 1000
  keepalive: 5
```

## Monitoring & Health Checks

### Health Check Endpoint
```python
# Custom health check
@app.route('/health')
def health_check():
    """SearXNG health status"""
    
    try:
        # Test Google search
        test_query = "test"
        params = {
            'q': test_query,
            'engines': 'google',
            'format': 'json'
        }
        
        response = requests.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'status': 'healthy',
                'engines': 'operational',
                'response_time': response.elapsed.total_seconds(),
                'results_count': len(data.get('results', []))
            }
        else:
            return {
                'status': 'degraded',
                'engines': 'limited',
                'error': f"HTTP {response.status_code}"
            }
            
    except Exception as e:
        return {
            'status': 'unhealthy',
            'engines': 'offline', 
            'error': str(e)
        }
```

### Metrics Collection
```yaml
# Enable metrics
general:
  enable_metrics: true

# Custom metrics endpoint
server:
  metrics_path: "/metrics"
  
# Logging configuration
logging:
  root:
    level: INFO
  searx:
    level: INFO
  werkzeug:
    level: WARNING
```

## Troubleshooting

### Common Issues

#### 1. Engine Not Working
```bash
# Test individual engine
curl "http://localhost:8080/search?q=test&engines=google&format=json"

# Check engine status
curl "http://localhost:8080/stats"

# Verify configuration
python -c "import yaml; print(yaml.safe_load(open('searx/settings.yml')))"
```

#### 2. CORS Issues
```yaml
# Enable CORS in settings.yml
server:
  cors:
    origins: ["*"]
    methods: ["GET", "POST"]
    headers: ["Content-Type"]
```

#### 3. Rate Limiting Problems
```yaml
# Adjust rate limits
server:
  limiter: false  # Disable for development
  
  # Or configure custom limits
  default_rate_limit:
    GET: "1000/hour"
    POST: "500/hour"
```

### Debug Mode
```bash
# Enable debug logging
export SEARXNG_DEBUG=1

# Run with verbose output
python searx/webapp.py --debug

# Check logs
tail -f /var/log/searxng/searxng.log
```

### Configuration Validation
```python
# Validate settings
python -c "
from searx import settings
print('Settings loaded successfully')
print(f'Enabled engines: {[e[\"name\"] for e in settings[\"engines\"] if not e.get(\"disabled\", False)]}')
"
```

This SearXNG configuration guide provides comprehensive setup instructions for implementing Google-only search results with privacy protection and performance optimization.
