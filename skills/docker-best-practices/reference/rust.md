# Rust

Rust emits a static binary against musl, or a dynamically linked one against glibc. The build is slow enough that dependency-layer caching matters more here than anywhere else.

## Dockerfile

`cargo-chef` exists because `cargo build` compiles dependencies and source in one step, so the naive Dockerfile rebuilds every crate on any source edit. Chef splits the dependency compile into its own cacheable layer.

```dockerfile
# Stage 1: Plan — compute a dependency-only recipe
FROM lukemathwalker/cargo-chef:latest-rust-1 AS chef
WORKDIR /src

FROM chef AS planner
COPY . .
RUN cargo chef prepare --recipe-path recipe.json

# Stage 2: Build dependencies, then the application
FROM chef AS build
COPY --from=planner /src/recipe.json recipe.json
# This layer is keyed on the recipe, so it survives any source-only change.
RUN cargo chef cook --release --recipe-path recipe.json
COPY . .
RUN cargo build --release --bin server

# Stage 3: Production
FROM gcr.io/distroless/cc-debian12:nonroot
COPY --from=build /src/target/release/server /app
USER 65532:65532
ENTRYPOINT ["/app"]
```

## Notes

- **`distroless/cc`, not `static`**, because the default `x86_64-unknown-linux-gnu` target links against glibc. `cc` carries libgcc and libstdc++.
- **For a truly static binary**, build against musl and you can then use `scratch` or `distroless/static`:
  ```dockerfile
  RUN rustup target add x86_64-unknown-linux-musl && \
      cargo build --release --target x86_64-unknown-linux-musl --bin server
  ```
  Worth it for the smallest possible image, but musl's allocator is measurably slower than glibc's under heavy multi-threaded allocation. Benchmark before adopting it for a hot service.
- **Without `cargo-chef`**, the equivalent trick is to copy `Cargo.toml`/`Cargo.lock`, create a dummy `src/main.rs`, build to populate the dependency cache, then delete it and copy real source. Chef does this more reliably, especially across workspaces.
- **Keep `target/` in `.dockerignore`.** A local debug build is often larger than the entire final image, and shipping it into the build context slows every build.
- **Strip the binary** with `strip = true` under `[profile.release]` in `Cargo.toml`, rather than a separate step.
