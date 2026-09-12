# ==============================================================================
# 🦅 BENGAL WINGS :: PLAYGROUND SHORTCUT RUNNER (run from playground/)
# Usage: make help | make build | make run | make clean
# (The full GCS lives in ../gcs — launch it with `make gcs` from the repo root.)
# ==============================================================================

.PHONY: all help setup build run clean

# Default Target
all: help

help:
	@echo "=================================================================="
	@echo " 🦅 BENGAL WINGS :: PLAYGROUND COMMAND SHORTCUTS"
	@echo "=================================================================="
	@echo "  make build     - Compile the bare-metal I2C sensor driver (host gcc)"
	@echo "  make run       - Run the Python Wi-Fi TCP telemetry server demo"
	@echo "  make clean     - Remove temporary build files and logs"
	@echo "  make setup     - Run the Jetson dependency/deployment script"
	@echo "------------------------------------------------------------------"
	@echo "  NOTE: run these targets from inside playground/ (cd playground)."
	@echo "  Individual examples have self-documented run commands in their"
	@echo "  README.md — or just 'python3 <file>' / 'rustc <file>' etc."
	@echo "=================================================================="

setup:
	@echo "[SHORTCUT]: Running Setup Script..."
	@bash 24_system_setup_and_deploy.sh

build:
	@echo "[SHORTCUT]: Compiling Bare-Metal I2C Driver for host smoke-build..."
	@gcc -O2 17_pcb_i2c_sensor_driver.c -o build_i2c_driver
	@echo "[SUCCESS]: ./build_i2c_driver built (host smoke binary)."

run:
	@echo "[SHORTCUT]: Launching Wi-Fi Telemetry Server (Ctrl+C to stop)..."
	@python3 18_wifi_tcp_socket_server.py

clean:
	@echo "[SHORTCUT]: Cleaning build artifacts and logs..."
	@rm -rf build_* ./logs/*.log
	@echo "[SUCCESS]: Playground cleaned."
