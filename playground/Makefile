# ==============================================================================
# 🦅 BENGAL WINGS :: SHORTCUT COMMAND RUNNER (MAKEFILE)
# Usage: make help, make setup, make build, make clean
# ==============================================================================

.PHONY: all setup build run clean help

# Default Target
all: help

help:
	@echo "=================================================================="
	@echo " 🦅 BENGAL WINGS :: AVAILABLE COMMAND SHORTCUTS                   "
	@echo "=================================================================="
	@echo "  make setup     - Install dependencies and permissions"
	@echo "  make build     - Compile all C/C++, Go, and Rust binaries"
	@echo "  make run       - Run the main telemetry server"
	@echo "  make clean     - Remove temporary build files and logs"
	@echo "=================================================================="

setup:
	@echo "[SHORTCUT]: Running Setup Script..."
	@bash scripts/24_system_setup_and_deploy.sh

build:
	@echo "[SHORTCUT]: Compiling Bare-Metal Drivers..."
	@gcc -O2 examples/17_pcb_i2c_sensor_driver.c -o build_i2c_driver
	@echo "[SUCCESS]: Binaries built successfully in root folder."

run:
	@echo "[SHORTCUT]: Launching Wi-Fi Telemetry Server..."
	@python3 examples/18_wifi_tcp_socket_server.py

clean:
	@echo "[SHORTCUT]: Cleaning build artifacts and logs..."
	@rm -rf build_* ./logs/*.log
	@echo "[SUCCESS]: Workspace Cleaned."