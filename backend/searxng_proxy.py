#!/usr/bin/env python3
"""
Simple Flask backend to serve as a proxy for SearXNG API calls from Flutter
Handles CORS and provides a clean API interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
import logging

app = Flask(__name__)

# Configure CORS to allow requests from everywhere
CORS(app, 
     resources={
         r"/*": {
             "origins": "*",
             "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "X-Real-IP", "X-Forwarded-For"],
             "supports_credentials": False
         }
     },
     expose_headers=["Content-Type"])

# Add a catch-all for preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Requested-With,X-Real-IP,X-Forwarded-For")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response, 200

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SearXNG configuration
SEARXNG_BASE_URL = os.environ.get('SEARXNG_URL', 'http://localhost:8080')
SEARXNG_SEARCH_ENDPOINT = '/search'

# Public SearXNG instances as fallback (reliable instances)
PUBLIC_INSTANCES = [
    'https://search.sapti.me',
    'https://searx.be',
    'https://searx.info',
    'https://search.mdosch.de',
    'https://searx.tiekoetter.com',
    'https://searx.fmac.xyz',
    'https://searx.namejeff.xyz'
]

def search_with_instance(instance_url, params, client_ip='127.0.0.1'):
    """Search using a specific SearXNG instance"""
    try:
        # Add proper proxy headers to prevent bot detection errors
        headers = {
            'User-Agent': 'Golligog-Flutter-Backend/1.0',
            'Accept': 'application/json',
            'X-Forwarded-For': client_ip,
            'X-Real-IP': client_ip,
            'X-Forwarded-Proto': 'http',
            'X-Forwarded-Host': 'localhost'
        }
        
        response = requests.get(
            f"{instance_url}{SEARXNG_SEARCH_ENDPOINT}",
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"Instance {instance_url} returned status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error with instance {instance_url}: {e}")
        return None

def filter_result_sources(result_data):
    """Remove source information from search results"""
    if not result_data or 'results' not in result_data:
        return result_data
    
    filtered_results = []
    for result in result_data['results']:
        # Create a clean result without engine/source information
        clean_result = {
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'publishedDate': result.get('publishedDate'),
            'thumbnail': result.get('thumbnail'),
            'template': result.get('template', 'default')
        }
        # Remove None values
        clean_result = {k: v for k, v in clean_result.items() if v is not None}
        filtered_results.append(clean_result)
    
    # Update the result data
    result_data['results'] = filtered_results
    
    # Remove engine information from the response
    if 'engines' in result_data:
        del result_data['engines']
    if 'answers' in result_data:
        del result_data['answers']
    if 'infoboxes' in result_data:
        del result_data['infoboxes']
    
    return result_data

@app.route('/api/search', methods=['GET', 'OPTIONS'])
@app.route('/search', methods=['GET', 'OPTIONS'])
def search():
    """Search endpoint that proxies to SearXNG with Google-only results"""
    if request.method == 'OPTIONS':
        return '', 204
    
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    # Get client IP for proper forwarding
    client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    
    # Map category to appropriate engines (fallback to multiple if one fails)
    category = request.args.get('category', 'general')
    engines_map = {
        'general': ['google', 'bing', 'duckduckgo'],
        'images': ['google_images', 'bing_images'],
        'news': ['google_news', 'bing_news'],
        'videos': ['google_videos', 'bing_videos'],
        'science': ['google_scholar', 'semantic_scholar'],
        'files': ['google_scholar'],
        'map': ['openstreetmap'],
    }
    
    # Get list of engines to try
    engines_to_try = engines_map.get(category, ['google', 'bing', 'duckduckgo'])
    
    # Search parameters - try multiple engines if one fails
    result = None
    for engine in engines_to_try:
        params = {
            'q': query,
            'format': 'json',
            'engines': engine,
            'lang': request.args.get('lang', 'en'),
            'pageno': request.args.get('page', '1'),
        }
        
        # Try local instance first
        result = search_with_instance(SEARXNG_BASE_URL, params, client_ip)
        
        if result and result.get('results'):
            logger.info(f"Got results from {engine} engine")
            break
        
        # If local instance fails, try public instances
        if not result:
            for instance in PUBLIC_INSTANCES:
                result = search_with_instance(instance, params, client_ip)
                if result and result.get('results'):
                    logger.info(f"Got results from {engine} engine on {instance}")
                    break
            
            if result and result.get('results'):
                break
    
    if result:
        # Filter out source information
        filtered_result = filter_result_sources(result)
        return jsonify(filtered_result)
    else:
        return jsonify({
            'error': 'All search instances are unavailable. Please try again later.',
            'query': query,
            'number_of_results': 0,
            'results': []
        }), 503

@app.route('/api/engines', methods=['GET', 'OPTIONS'])
def engines():
    """Get available engines from SearXNG"""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Get client IP for proper forwarding
        client_ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
        
        headers = {
            'User-Agent': 'Golligog-Flutter-Backend/1.0',
            'Accept': 'application/json',
            'X-Forwarded-For': client_ip,
            'X-Real-IP': client_ip,
            'X-Forwarded-Proto': 'http',
            'X-Forwarded-Host': 'localhost'
        }
        
        response = requests.get(
            f"{SEARXNG_BASE_URL}/engines",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify([])  # Return empty list if engines endpoint fails
    except Exception as e:
        print(f"Error getting engines: {e}")
        return jsonify([])

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
    
    # Check if local SearXNG instance is available
    local_healthy = False
    try:
        response = requests.get(f"{SEARXNG_BASE_URL}/healthz", timeout=3)
        local_healthy = response.status_code == 200
    except:
        pass
    
    # Check at least one public instance
    public_healthy = False
    for instance in PUBLIC_INSTANCES[:2]:  # Check first 2 instances
        try:
            response = requests.get(f"{instance}/", timeout=3)
            if response.status_code == 200:
                public_healthy = True
                break
        except:
            continue
    
    return jsonify({
        'status': 'healthy' if (local_healthy or public_healthy) else 'unhealthy',
        'local_instance': local_healthy,
        'public_instances_available': public_healthy,
        'searxng_url': SEARXNG_BASE_URL
    })

@app.route('/', methods=['GET'])
def index():
    """API information endpoint"""
    return jsonify({
        'name': 'Golligog SearXNG Backend',
        'version': '1.0.0',
        'description': 'Flask backend proxy for SearXNG search API',
        'endpoints': {
            '/api/search': 'Search endpoint (GET with ?q=query)',
            '/api/engines': 'Get available search engines',
            '/api/health': 'Health check'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Golligog SearXNG Backend on port {port}")
    print(f"SearXNG URL: {SEARXNG_BASE_URL}")
    print(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
