# === Configuration ===
PY_APP_DIR := app
ARDUINO_DIR := arduino

# === Python App Commands ===

.PHONY: install
install:
	cd $(PY_APP_DIR) && poetry install

.PHONY: run
run:
	cd $(PY_APP_DIR)/src && poetry run python growzucchini/main.py

.PHONY: test
test:
	cd $(PY_APP_DIR)/src && poetry run pytest

.PHONY: lint
lint:
	cd $(PY_APP_DIR)/src && poetry run ruff check growzucchini tests

# === Arduino Commands ===

.PHONY: build-arduino
build-arduino:
	cd $(ARDUINO_DIR) && platformio run

.PHONY: upload-arduino
upload-arduino:
	cd $(ARDUINO_DIR) && platformio run --target upload

.PHONY: monitor-arduino
monitor-arduino:
	cd $(ARDUINO_DIR) && platformio device monitor

# === Docker ===

.PHONY: up
up:
	cd $(PY_APP_DIR) && docker compose up -d

.PHONY: down
down:
	cd $(PY_APP_DIR) && docker compose down

# === All ===

.PHONY: all
all: install build-arduino
