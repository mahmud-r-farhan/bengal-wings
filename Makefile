# ==============================================================================
# 🦅 BENGAL WINGS — MASTER SHORTCUT RUNNER (repository root)
# Usage: make help | make gcs | make test | make check | make clean
# ==============================================================================

PYTHON   ?= python3
GCS_PORT ?= 8090

.PHONY: all help gcs gcs-pad test check clean

all: help

help:
	@echo "=================================================================="
	@echo " 🦅 BENGAL WINGS :: AVAILABLE COMMAND SHORTCUTS"
	@echo "=================================================================="
	@echo "  make gcs       - Launch the Phase-1 GCS (telemetry server + dashboard)"
	@echo "  make gcs-pad   - Same, but the vehicle starts disarmed on the pad"
	@echo "  make test      - Run the GCS unit-test suite (22 tests, stdlib only)"
	@echo "  make check     - Byte-compile all Python sources (syntax gate)"
	@echo "  make clean     - Remove caches and local build artifacts"
	@echo "------------------------------------------------------------------"
	@echo "  playground/    - 25 standalone module examples (see playground/Makefile)"
	@echo "=================================================================="

gcs:
	@echo "[GCS] Launching Bengal Wings Ground Control Station on port $(GCS_PORT)..."
	@$(PYTHON) -m gcs --port $(GCS_PORT)

gcs-pad:
	@$(PYTHON) -m gcs --port $(GCS_PORT) --no-auto-demo

test:
	@$(PYTHON) -m unittest discover -s tests -v

check:
	@$(PYTHON) -m compileall -q gcs tests
	@echo "[OK] All Python modules compile cleanly."

clean:
	@find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build_* logs/*.log 2>/dev/null || true
	@echo "[OK] Workspace cleaned."
