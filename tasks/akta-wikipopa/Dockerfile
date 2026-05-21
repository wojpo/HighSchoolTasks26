FROM rust:latest

RUN rustup target add wasm32-unknown-unknown
RUN cargo install trunk
RUN cargo install miniserve

WORKDIR /app
COPY src/ .
RUN trunk build --release

EXPOSE 3000
CMD ["miniserve", "/app/dist", "-p", "3000", "--index", "index.html", "--spa"]
