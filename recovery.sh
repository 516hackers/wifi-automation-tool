#!/bin/bash

# Emergency Recovery Script for WiFi Automation Tool
# Use when Python environment is broken

echo "🆘 EMERGENCY RECOVERY MODE"
echo "=========================="

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Fix APT issues
fix_apt() {
    log "Fixing APT issues..."
    
    # Kill any stuck apt processes
    pkill -f apt
    pkill -f dpkg
    
    # Remove lock files
    rm -f /var/lib/dpkg/lock*
    rm -f /var/lib/apt/lists/lock*
    rm -f /var/cache/apt/archives/lock*
    
    # Fix broken packages
    dpkg --configure -a
    apt --fix-broken install -y
    
    # Clean up
    apt clean
    apt autoclean
    
    # Update
    apt update
}

# Fix network issues
fix_network() {
    log "Fixing network issues..."
    
    # Restart network services
    systemctl restart NetworkManager
    systemctl restart networking
    systemctl restart wpa_supplicant
    
    # Reset network interfaces
    ip link set wlan0 down 2>/dev/null
    ip link set wlan0 up 2>/dev/null
    
    # Unblock RFKILL
    rfkill unblock all
}

# Fix driver issues
fix_drivers() {
    log "Fixing driver issues..."
    
    # Install essential WiFi packages
    apt install -y --allow-downgrades --allow-remove-essential \
        firmware-linux \
        firmware-linux-nonfree \
        wireless-tools \
        wpasupplicant \
        net-tools
    
    # Load WiFi modules
    modprobe -r ath9k ath9k_common ath9k_hw
    modprobe ath9k
    modprobe ath9k_common
    modprobe ath9k_hw
}

# Main recovery function
main_recovery() {
    log "Starting comprehensive system recovery..."
    
    # Fix APT first
    fix_apt
    
    # Fix network
    fix_network
    
    # Fix drivers
    fix_drivers
    
    # Final cleanup
    apt autoremove -y
    apt autoclean
    
    log "Recovery completed! Try running the main tool again."
}

# Run recovery
main_recovery

echo "=================================="
echo "🔧 Recovery process completed"
echo "🚀 Run: sudo ./main.py"
