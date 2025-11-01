#!/bin/bash
# Golligog Search Engine - Complete System Startup (Linux/Ubuntu/macOS)
# Starts Docker (SearXNG + Redis) and Flask Backend concurrently
# With health checks and proper error handling

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $(date '+%H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $(date '+%H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $(date '+%H:%M:%S') - $1"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Cleanup function
cleanup() {
    log_info "Shutting down services..."
    
    # Stop Flask backend
    if [ ! -z "$FLASK_PID" ] && kill -0 $FLASK_PID 2>/dev/null; then
        log_info "Stopping Flask Backend (PID: $FLASK_PID)"
        kill $FLASK_PID 2>/dev/null || true
    fi
    
    # Stop Docker containers
    if docker ps | grep -q "golligog-searxng"; then
        log_info "Stopping Docker containers"
        docker compose -f "$PROJECT_ROOT/docker-compose.yml" down 2>/dev/null || true
    fi
    
    log_success "System shutdown complete"
}

# Trap signals for graceful shutdown
trap cleanup EXIT INT TERM

# Check if Docker is installed
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo "Install Docker from: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    log_success "Docker is installed"
}

# Check if Docker daemon is running
check_docker_daemon() {
    log_info "Checking Docker daemon..."
    
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        echo "Start Docker with: sudo systemctl start docker"
        exit 1
    fi
    
    log_success "Docker daemon is running"
}

# Check if docker-compose is available
check_docker_compose() {
    log_info "Checking Docker Compose..."
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version > /dev/null 2>&1; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_success "Docker Compose is available"
}

# Check if Python is installed
check_python() {
    log_info "Checking Python installation..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION is installed"
}

# Check port availability
check_port() {
    local port=$1
    local service=$2
    
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        log_warning "Port $port (${service}) may be in use"
        return 1
    fi
    return 0
}

# Check ports
check_ports() {
    log_info "Checking port availability..."
    
    local ports_ok=true
    
    if ! check_port 8080 "SearXNG"; then
        ports_ok=false
    fi
    
    if ! check_port 5000 "Flask Backend"; then
        ports_ok=false
    fi
    
    if ! check_port 6379 "Redis"; then
        ports_ok=false
    fi
    
    if [ "$ports_ok" = true ]; then
        log_success "All required ports are available"
    else
        log_warning "Some ports may be in use, continuing anyway..."
    fi
}

# Start Docker services
start_docker() {
    log_info "Step 1/4: Starting Docker services (SearXNG + Redis)..."
    
    cd "$PROJECT_ROOT"
    
    if docker compose up -d > /dev/null 2>&1; then
        log_success "Docker services started"
    else
        log_error "Failed to start Docker services"
        docker compose logs --tail 20
        exit 1
    fi
}

# Wait for service with retry
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_retries=${3:-30}
    local retry_interval=${4:-2}
    
    log_info "Waiting for $service_name..."
    
    for ((i = 1; i <= max_retries; i++)); do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$service_name is ready!"
            return 0
        fi
        
        if [ $i -lt $max_retries ]; then
            echo -ne "  Attempt $i/$max_retries...\r"
            sleep $retry_interval
        fi
    done
    
    log_error "$service_name failed to start after $((max_retries * retry_interval)) seconds"
    return 1
}

# Wait for SearXNG
wait_for_searxng() {
    log_info "Step 2/4: Waiting for SearXNG to be healthy..."
    
    if wait_for_service "http://localhost:8080" "SearXNG" 30 2; then
        return 0
    else
        log_error "SearXNG failed to start. Checking logs..."
        docker logs golligog-searxng | tail -20
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    log_info "Checking Python dependencies..."
    
    if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found in $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    if python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
        log_success "All dependencies are installed"
    else
        log_warning "Installing/updating dependencies..."
        python3 -m pip install -q -r requirements.txt
        log_success "Dependencies installed"
    fi
}

# Start Flask backend
start_flask() {
    log_info "Step 3/4: Starting Flask Backend..."
    
    cd "$BACKEND_DIR"
    
    # Start Flask in background
    nohup python3 searxng_proxy.py > "$PROJECT_ROOT/flask_backend.log" 2>&1 &
    FLASK_PID=$!
    
    # Give Flask time to start
    sleep 3
    
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        log_error "Flask Backend failed to start"
        cat "$PROJECT_ROOT/flask_backend.log"
        exit 1
    fi
    
    log_success "Flask Backend started (PID: $FLASK_PID)"
}

# Wait for Flask backend
wait_for_flask() {
    if wait_for_service "http://localhost:5000/api/health" "Flask Backend" 10 1; then
        return 0
    else
        log_error "Flask Backend failed to start or is not responding"
        cat "$PROJECT_ROOT/flask_backend.log"
        exit 1
    fi
}

# Verify all services
verify_services() {
    log_info "Step 4/4: Verifying all services..."
    
    local all_ok=true
    
    # Check SearXNG
    if curl -s "http://localhost:8080" > /dev/null 2>&1; then
        log_success "SearXNG is responding"
    else
        log_error "SearXNG is not responding"
        all_ok=false
    fi
    
    # Check Flask
    if curl -s "http://localhost:5000/api/health" > /dev/null 2>&1; then
        log_success "Flask Backend is responding"
    else
        log_error "Flask Backend is not responding"
        all_ok=false
    fi
    
    # Check Redis
    if docker ps | grep -q "golligog-redis.*Up"; then
        log_success "Redis is running"
    else
        log_error "Redis is not running"
        all_ok=false
    fi
    
    if [ "$all_ok" = false ]; then
        exit 1
    fi
}

# Display summary
display_summary() {
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ SYSTEM STARTUP COMPLETE${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}Available Services:${NC}"
    echo "  • SearXNG:         http://localhost:8080"
    echo "  • Flask Backend:   http://localhost:5000"
    echo "  • Redis:           localhost:6379 (Docker)"
    echo ""
    echo -e "${CYAN}API Endpoints:${NC}"
    echo "  • Search:          http://localhost:5000/api/search?q=<query>"
    echo "  • Health Check:    http://localhost:5000/api/health"
    echo "  • Engines List:    http://localhost:5000/api/engines"
    echo ""
    echo -e "${CYAN}Next Steps:${NC}"
    echo "  1. Run Flutter app:    flutter run -d chrome"
    echo "  2. Test in browser:    http://localhost:49686"
    echo "  3. View SearXNG logs:  docker logs -f golligog-searxng"
    echo "  4. View Flask logs:    tail -f $PROJECT_ROOT/flask_backend.log"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Starting Golligog Search Engine System${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Pre-flight checks
    check_docker
    check_docker_daemon
    check_docker_compose
    check_python
    check_ports
    
    echo ""
    
    # Installation and startup
    install_dependencies
    start_docker
    wait_for_searxng
    start_flask
    wait_for_flask
    verify_services
    
    echo ""
    
    display_summary
    
    # Keep script running
    while true; do
        sleep 1
        
        # Check if Flask is still running
        if ! kill -0 $FLASK_PID 2>/dev/null; then
            log_error "Flask Backend process died!"
            log_info "Restarting Flask Backend..."
            start_flask
            wait_for_flask
        fi
    done
}

# Run main function
main