# Build stage (keep existing setup until venv creation)
FROM debian:bookworm-slim AS builder

SHELL ["bash", "-exc"]

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive 

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /usr/local/bin/uv

RUN uv venv /opt/venv --python python3.11
ENV VIRTUAL_ENV=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_CACHE_DIR=/opt/venv/.cache 

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libpq-dev \
    curl \
    pkg-config \
    libssl-dev \
    zlib1g-dev \
    libclang-dev \
    clang \
    cmake \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:/opt/venv/bin:${PATH}"
ENV RUSTFLAGS="-C codegen-units=4 -C opt-level=0 -C debuginfo=0"

COPY pyproject.toml .
COPY uv.lock . 
RUN uv pip install maturin && \
    uv pip install -e .

# copy .so from cache to package
RUN find /opt/venv/.cache -name *.so -path *bindings/extractous* ! -path *release* -print -exec cp {} /opt/venv/lib/python3.11/site-packages/extractous/ \;

# Clean Rust artifacts
RUN rm -rf /root/.cargo/registry /root/.cargo/git

########### Runtime stage #######################################################
FROM debian:bookworm-slim AS runtime

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive \
    PATH="/root/.cargo/bin:/opt/venv/bin:${PATH}" \
    UV_CACHE_DIR=/opt/venv/.cache

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /root/.local/share/uv/python /root/.local/share/uv/python

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
# COPY entrypoint.sh /entrypoint.sh

# Set execute permissions for entrypoint
RUN chmod +x /app/entrypoint.sh

# Ownership/User setup removed as per previous steps

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
ENV PYTHONPATH=/app:$PYTHONPATH

# Container runs as root
ENTRYPOINT ["/app/entrypoint.sh"]