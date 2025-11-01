#!/usr/bin/env python3
"""
Quick SearXNG Setup for Golligog - Minimal Configuration
This script creates a minimal SearXNG setup that works with the Flask backend
"""

import os
import sys
import tempfile
import subprocess

def create_minimal_searxng_settings():
    """Create minimal settings.yml for SearXNG"""
    settings_content = """# Minimal SearXNG configuration for Golligog
use_default_settings: true

general:
  debug: false
  instance_name: "Golligog Search"
  privacypolicy_url: false
  donation_url: false
  contact_url: false
  enable_metrics: false

brand:
  new_issue_url: false
  docs_url: false
  public_instances: false
  wiki_url: false
  issue_url: false

search:
  safe_search: 0
  autocomplete: ""
  default_lang: "en"
  max_page: 0
  formats: ["json", "html"]

server:
  port: 8080
  bind_address: "127.0.0.1"
  base_url: "http://localhost:8080/"
  secret_key: "golligog-search-secret-key-change-in-production"
  limiter: false
  public_instance: false
  image_proxy: false
  http_protocol_version: "1.1"
  method: "POST"

# Disable Redis for simplicity
redis:
  url: false

ui:
  static_use_hash: false
  default_locale: "en"
  query_in_title: false
  infinite_scroll: false
  center_alignment: false
  default_theme: "simple"
  theme_args:
    simple_style: "auto"

outgoing:
  request_timeout: 5.0
  useragent_suffix: "Golligog"
  pool_connections: 100
  pool_maxsize: 20
  enable_http2: true

# Enable only Google engines
engines:
  - name: google
    engine: google
    shortcut: go
    use_mobile_ui: false
    disabled: false
    timeout: 5.0
    
  - name: google images
    engine: google_images
    shortcut: goi
    disabled: false
    timeout: 5.0
    
  - name: google news
    engine: google_news
    shortcut: gon
    disabled: false
    timeout: 5.0
    
  - name: google videos
    engine: google_videos
    shortcut: gov
    disabled: false
    timeout: 5.0
    
  - name: google scholar
    engine: google_scholar
    shortcut: gos
    disabled: false
    timeout: 5.0

# Disable bot detection to prevent proxy header errors
botdetection:
  ip_lists:
    pass_searxng_org: false
  ip_limit:
    filter_link_local: false
    link_token: false
"""
    return settings_content

def setup_and_run_searxng():
    """Setup and run SearXNG with minimal configuration"""
    print("Setting up minimal SearXNG configuration...")
    
    # Create a temporary directory for SearXNG
    with tempfile.TemporaryDirectory() as temp_dir:
        searxng_dir = os.path.join(temp_dir, 'searxng')
        
        print("Cloning SearXNG...")
        result = subprocess.run([
            'git', 'clone', 'https://github.com/searxng/searxng.git', searxng_dir
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Failed to clone SearXNG: {result.stderr}")
            return False
        
        # Create settings file
        settings_path = os.path.join(searxng_dir, 'searx', 'settings.yml')
        with open(settings_path, 'w') as f:
            f.write(create_minimal_searxng_settings())
        
        print("Installing SearXNG dependencies...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-U', 
            'pip', 'setuptools', 'wheel', 'pyyaml', 'lxml'
        ], cwd=searxng_dir)
        
        if result.returncode != 0:
            print("Failed to install dependencies")
            return False
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-e', '.'
        ], cwd=searxng_dir)
        
        if result.returncode != 0:
            print("Failed to install SearXNG")
            return False
        
        # Set environment variable
        os.environ['SEARXNG_SETTINGS_PATH'] = settings_path
        
        print("Starting SearXNG server on http://localhost:8080")
        print("Press Ctrl+C to stop")
        
        try:
            webapp_path = os.path.join(searxng_dir, 'searx', 'webapp.py')
            subprocess.run([sys.executable, webapp_path], cwd=searxng_dir)
        except KeyboardInterrupt:
            print("\nSearXNG server stopped")
        
        input("Press Enter to exit...")
    
    return True

if __name__ == '__main__':
    setup_and_run_searxng()