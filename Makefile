# Define variables
CARGO = cargo
RUSTFLAGS = --all-features
PROJECT_NAME = thiskb

# Default target
.PHONY: build
default: build

# shortcuts
.PHONY: r
r: dev
.PHONY: c
c: check fmt
.PHONY: fmt
fmt: format clippy

# Development target
.PHONY: dev
dev:
	$(CARGO) r $(RUSTFLAGS) watch

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
