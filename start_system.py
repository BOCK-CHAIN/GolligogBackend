#!/usr/bin/env python3
"""
Complete startup script for Golligog Search Engine
Starts Docker (SearXNG + Redis) and Flask Backend concurrently
With health checks and proper error handling
"""

import subprocess
import time
import requests
import sys
import os
from pathlib import Path
import signal
import threading
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    CYAN = '\033[96m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {datetime.now().strftime('%H:%M:%S')} - {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[✓]{Colors.RESET} {datetime.now().strftime('%H:%M:%S')} - {msg}")

def log_error(msg):
    print(f"{Colors.RED}[✗]{Colors.RESET} {datetime.now().strftime('%H:%M:%S')} - {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[!]{Colors.RESET} {datetime.now().strftime('%H:%M:%S')} - {msg}")

def run_command(cmd, shell=True, cwd=None):
    """Run a command and return the process"""
    try:
        return subprocess.Popen(
            cmd,
            shell=shell,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except Exception as e:
        log_error(f"Failed to run command: {e}")
        return None

def check_service_health(url, service_name, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            log_success(f"{service_name} is responding")
            return True
        else:
            log_warning(f"{service_name} returned status {response.status_code}")
            return False
    except Exception as e:
        log_warning(f"{service_name} not responding: {e}")
        return False

def wait_for_service(url, service_name, max_retries=30, retry_interval=2):
    """Wait for a service to be available"""
    log_info(f"Waiting for {service_name}...")
    
    for attempt in range(max_retries):
        if check_service_health(url, service_name, timeout=2):
            log_success(f"{service_name} is ready!")
            return True
        
        if attempt < max_retries - 1:
            print(f"  Attempt {attempt + 1}/{max_retries}...", end='\r')
            time.sleep(retry_interval)
    
    log_error(f"{service_name} failed to start after {max_retries * retry_interval} seconds")
    return False

def cleanup_on_exit(processes):
    """Cleanup function to stop all processes"""
    log_info("Shutting down services...")
    for name, process in processes.items():
        if process and process.poll() is None:
            try:
                process.terminate()
                log_info(f"Stopped {name}")
            except:
                pass

def signal_handler(signum, frame, processes):
    """Handle Ctrl+C gracefully"""
    print(f"\n{Colors.YELLOW}Received interrupt signal...{Colors.RESET}")
    cleanup_on_exit(processes)
    sys.exit(0)

def main():
    """Main startup orchestration"""
    
    log_info("=" * 60)
    log_info("Starting Golligog Search Engine System")
    log_info("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    backend_dir = project_root / 'backend'
    
    # Check if backend directory exists
    if not backend_dir.exists():
        log_error(f"Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    # Dictionary to store processes
    processes = {}
    
    try:
        # Step 1: Start Docker services
        log_info("Step 1/3: Starting Docker services (SearXNG + Redis)...")
        
        docker_process = run_command(
            'docker compose up -d',
            shell=True,
            cwd=str(project_root)
        )
        
        if docker_process:
            stdout, stderr = docker_process.communicate()
            
            if docker_process.returncode == 0:
                log_success("Docker services started")
                processes['docker'] = None  # Docker runs in background
            else:
                log_error(f"Docker startup failed: {stderr}")
                sys.exit(1)
        
        # Step 2: Wait for SearXNG to be ready
        log_info("Step 2/3: Waiting for SearXNG to be healthy...")
        if not wait_for_service('http://localhost:8080', 'SearXNG', max_retries=30):
            log_error("SearXNG failed to start. Checking Docker logs...")
            subprocess.run('docker logs golligog-searxng | tail -20', shell=True)
            sys.exit(1)
        
        # Step 3: Start Flask backend
        log_info("Step 3/3: Starting Flask Backend...")
        
        flask_process = run_command(
            f'{sys.executable} searxng_proxy.py',
            shell=True,
            cwd=str(backend_dir)
        )
        
        if not flask_process:
            log_error("Failed to start Flask backend")
            sys.exit(1)
        
        processes['flask'] = flask_process
        
        # Wait a bit for Flask to start
        time.sleep(3)
        
        # Check Flask backend health
        if not wait_for_service('http://localhost:5000/api/health', 'Flask Backend', max_retries=10):
            log_error("Flask Backend failed to start")
            log_warning("Checking Flask output...")
            stderr = flask_process.stderr.read() if flask_process.stderr else "No error output"
            log_error(f"Flask error: {stderr}")
            sys.exit(1)
        
        # Step 4: Verify all services
        log_info("Step 4/4: Verifying all services...")
        
        services_status = {
            'SearXNG': 'http://localhost:8080',
            'Flask Backend': 'http://localhost:5000/api/health',
            'Redis': 'docker ps | findstr golligog-redis'  # Docker check
        }
        
        all_healthy = True
        for service, check in services_status.items():
            if 'docker' in check.lower():
                result = subprocess.run(check, shell=True, capture_output=True)
                if result.returncode == 0:
                    log_success(f"{service} is running")
                else:
                    log_error(f"{service} is not running")
                    all_healthy = False
            else:
                if check_service_health(check, service):
                    pass  # Already logged
                else:
                    all_healthy = False
        
        if not all_healthy:
            log_warning("Some services may not be fully operational")
        
        # Display summary
        print(f"\n{Colors.GREEN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.GREEN}✓ SYSTEM STARTUP COMPLETE{Colors.RESET}")
        print(f"{Colors.GREEN}{'=' * 60}{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}Available Services:{Colors.RESET}")
        print(f"  • SearXNG:         http://localhost:8080")
        print(f"  • Flask Backend:   http://localhost:5000")
        print(f"  • Redis:           localhost:6379 (Docker)\n")
        
        print(f"{Colors.CYAN}API Endpoints:{Colors.RESET}")
        print(f"  • Search:          http://localhost:5000/api/search?q=<query>")
        print(f"  • Health Check:    http://localhost:5000/api/health")
        print(f"  • Engines List:    http://localhost:5000/api/engines\n")
        
        print(f"{Colors.CYAN}Next Steps:{Colors.RESET}")
        print(f"  1. Run Flutter app: flutter run -d chrome")
        print(f"  2. Test in browser: http://localhost:49686 (Flutter dev server)")
        print(f"  3. View logs:       docker logs -f golligog-searxng\n")
        
        print(f"{Colors.YELLOW}Press Ctrl+C to stop all services{Colors.RESET}\n")
        
        # Setup signal handler for graceful shutdown
        def signal_handler_wrapper(signum, frame):
            signal_handler(signum, frame, processes)
        
        signal.signal(signal.SIGINT, signal_handler_wrapper)
        
        # Keep the Flask process running
        while True:
            time.sleep(1)
            
            # Check if Flask process is still running
            if flask_process.poll() is not None:
                log_error("Flask Backend process died!")
                log_error("Restarting Flask Backend...")
                flask_process = run_command(
                    f'{sys.executable} searxng_proxy.py',
                    shell=True,
                    cwd=str(backend_dir)
                )
                if flask_process:
                    processes['flask'] = flask_process
                    time.sleep(3)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup_on_exit(processes)
        log_info("System shutdown complete")

if __name__ == '__main__':
    main()