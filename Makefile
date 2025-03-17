# Define variables
CARGO = cargo
RUSTFLAGS = 
PROJECT_NAME = thiskb

# Default target
.PHONY: build
default: build

# shortcuts
.PHONY: r
r: dev
.PHONY: c
c: check fmt b
.PHONY: fmt
fmt: format clippy
.PHONY: b
b: bacon

# Development target
.PHONY: dev
dev:
	uv run --env-file .env manage.py runserver

.PHONY: check
check:
	$(CARGO) check $(RUSTFLAGS)

# Build target
.PHONY: build
build:
	$(CARGO) build --release $(RUSTFLAGS)

# Format target
.PHONY: format
format:
	$(CARGO) fmt

# run clippy
.PHONY: clippy
clippy:
	$(CARGO) clippy

# Deploy target
.PHONY: deploy
deploy:
