VENV := .venv
PYTHON := python3
VENV_PY := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

.PHONY: help venv install run clean

help:
	@echo "Targets:"
	@echo "  make venv    - Create virtual environment"
	@echo "  make install - Install dependencies into venv"
	@echo "  make run     - Run the game"
	@echo "  make clean   - Remove virtual environment"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PIP) install -r requirements.txt

run: install
	cd src && ../$(VENV_PY) main.py

clean:
	rm -rf $(VENV)
