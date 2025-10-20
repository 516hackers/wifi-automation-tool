#!/bin/bash

# WiFi Automation Tool Installer for Kali Linux

echo "🔧 Installing WiFi Automation Tool..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root (sudo ./install.sh)"
    exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "📥 Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
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
    git \
    curl \
    wget

# Create virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv wifi-env
source wifi-env/bin/activate

# Install Python packages
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Make main script executable
chmod +x main.py

# Create necessary directories
mkdir -p logs drivers config

# Install additional WiFi tools
echo "📡 Installing WiFi tools..."
apt install -y \
    aircrack-ng \
    reaver \
    bully \
    pixiewps \
    hcxtools \
    hcxdumptool

# Load WiFi modules
echo "🔌 Loading WiFi modules..."
modprobe -r ath9k ath9k_common ath9k_hw ath10k_pci
modprobe ath9k
modprobe ath9k_common
modprobe ath9k_hw
modprobe ath10k_pci

echo "✅ Installation completed!"
echo "🚀 Run the tool with: sudo ./main.py"
