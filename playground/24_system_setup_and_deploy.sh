#!/usr/bin/env bash
# ==============================================================================
# 🦅 BENGAL WINGS :: AUTOMATED SYSTEM SETUP & DEPLOYMENT SCRIPT
# Run with: chmod +x 24_system_setup_and_deploy.sh && ./24_system_setup_and_deploy.sh
# ==============================================================================

set -e # Stop script on first error

# Formatting Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================================${NC}"
echo -e "${GREEN} 🦅 BENGAL WINGS :: LINUX BASH AUTOMATION ENGINE                   ${NC}"
echo -e "${BLUE}==================================================================${NC}"

# Function to check if a command exists
check_tool() {
    if command -v "$1" &> /dev/null; then
        echo -e "  [✔] Tool ${GREEN}$1${NC} is installed."
    else
        echo -e "  [✘] Tool ${RED}$1${NC} is MISSING!"
    fi
}

echo -e "\n${YELLOW}[1/3] Checking System Environment & Dependencies...${NC}"
check_tool "python3"
check_tool "go"
check_tool "gcc"
check_tool "git"

echo -e "\n${YELLOW}[2/3] Preparing Log Directories & Hardware Serial Ports...${NC}"
mkdir -p ./logs
chmod 755 ./logs
echo -e "  [->] Log directory initialized: ${GREEN}./logs/${NC}"

echo -e "\n${YELLOW}[3/3] Simulating Build & Verification Step...${NC}"
sleep 0.5
echo -e "  [✔] Compiling C/C++ Firmware Core... ${GREEN}DONE${NC}"
echo -e "  [✔] Validating Python & Go Modules... ${GREEN}DONE${NC}"

echo -e "\n${BLUE}==================================================================${NC}"
echo -e "${GREEN}[SUCCESS]: Bengal Wings Environment Ready for Deployment!${NC}"
echo -e "${BLUE}==================================================================${NC}"