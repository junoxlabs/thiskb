FROM rust:1.74-slim AS builder

WORKDIR /usr/src/

COPY . .

RUN cargo build --release


#####################################################################################

FROM debian:bookworm-slim AS runner

WORKDIR /usr/app

COPY --from=builder /usr/src/config /usr/app/config
COPY --from=builder /usr/src/target/release/thiskb-cli /usr/app/thiskb-cli

ENTRYPOINT ["/usr/app/thiskb-cli"]
