#!/bin/bash

# Enhanced WiFi Automation Tool Installer for Kali Linux

echo "🔧 Installing Enhanced WiFi Automation Tool..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    error "Please run as root: sudo $0"
    exit 1
fi

# System health check
system_health_check() {
    log "Running system health check..."
    
    # Check disk space
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 1048576 ]; then  # Less than 1GB
        warn "Low disk space detected. Attempting cleanup..."
        apt clean
        apt autoclean
    fi
    
    # Check for broken packages
    if dpkg -l | grep -q '^rc'; then
        warn "Found broken packages. Attempting repair..."
        dpkg --configure -a
        apt --fix-broken install -y
    fi
}

# Fix common APT issues
fix_apt_issues() {
    log "Checking and fixing APT issues..."
    
    # Remove lock files
    rm -f /var/lib/dpkg/lock*
    rm -f /var/lib/apt/lists/lock*
    rm -f /var/cache/apt/archives/lock*
    
    # Configure pending packages
    dpkg --configure -a
    
    # Fix broken installations
    apt --fix-broken install -y
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Update system
    apt update && apt upgrade -y
    
    # Install essential packages
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-apt \
        wireless-tools \
        wpasupplicant \
        net-tools \
        pciutils \
        usbutils \
        firmware-linux \
        firmware-linux-nonfree \
        firmware-atheros \
        firmware-realtek \
        firmware-iwlwifi \
        firmware-brcm80211 \
        git \
        curl \
        wget \
        dkms \
        build-essential \
        linux-headers-$(uname -r) \
        psutil
    
    # Install WiFi tools
    apt install -y \
        aircrack-ng \
        reaver \
        bully \
        pixiewps \
        hcxtools \
        hcxdumptool \
        iw \
        rfkill
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv wifi-env
    
    # Activate and install packages
    source wifi-env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install psutil if not in requirements
    pip install psutil
}

# Setup project structure
setup_project() {
    log "Setting up project structure..."
    
    # Create necessary directories
    mkdir -p logs drivers config backups
    
    # Make scripts executable
    chmod +x main.py
    chmod +x recovery.sh
    chmod +x install.sh
    
    # Create backup of important files
    log "Creating backups of system files..."
    cp /etc/apt/sources.list backups/sources.list.backup.$(date +%s) 2>/dev/null || true
    cp /etc/NetworkManager/NetworkManager.conf backups/NetworkManager.conf.backup.$(date +%s) 2>/dev/null || true
}

# Load WiFi modules
load_wifi_modules() {
    log "Loading WiFi modules..."
    
    modules=(
        "ath9k"
        "ath9k_common" 
        "ath9k_hw"
        "ath10k_pci"
        "rt2800usb"
        "rt2x00usb"
        "iwlwifi"
        "rtl8192cu"
        "rtl8xxxu"
    )
    
    for module in "${modules[@]}"; do
        modprobe "$module" 2>/dev/null && log "Loaded $module" || warn "Failed to load $module"
    done
    
    # Unblock all RFKILL
    rfkill unblock all
}

# Test installation
test_installation() {
    log "Testing installation..."
    
    # Test Python setup
    if source wifi-env/bin/activate && python3 -c "import psutil; print('Python environment OK')"; then
        log "Python environment test passed"
    else
        error "Python environment test failed"
        exit 1
    fi
    
    # Test WiFi tools
    if command -v iwconfig >/dev/null && command -v iw >/dev/null; then
        log "WiFi tools test passed"
    else
        error "WiFi tools test failed"
        exit 1
    fi
}

# Main installation process
main_installation() {
    log "Starting enhanced installation process..."
    
    # Run health check first
    system_health_check
    
    # Fix APT issues
    fix_apt_issues
    
    # Install dependencies
    install_dependencies
    
    # Setup Python environment
    setup_python_env
    
    # Setup project structure
    setup_project
    
    # Load WiFi modules
    load_wifi_modules
    
    # Test installation
    test_installation
    
    log "Installation completed successfully!"
    info "Usage:"
    info "  Normal use: sudo ./main.py"
    info "  Health check: sudo ./main.py --health-check"
    info "  System repair: sudo ./main.py --system-repair"
    info "  Emergency recovery: sudo ./recovery.sh"
}

# Run installation
main_installation

echo "================================================"
echo "🚀 Enhanced WiFi Automation Tool Ready!"
echo "================================================"
