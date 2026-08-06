# Go

Go emits a static binary, so the final image needs nothing but the binary itself. Expect 10–20MB.

## Dockerfile

```dockerfile
# Stage 1: Build
FROM golang:1.26-alpine AS build
WORKDIR /src

# Dependencies resolve from the manifest alone, so this layer survives source edits.
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# CGO_ENABLED=0 forces a static binary; without it the result needs libc and
# cannot run on scratch. -trimpath keeps build paths out of the binary.
RUN CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /app ./cmd/server

# Stage 2: Production
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /app /app
USER 65532:65532
ENTRYPOINT ["/app"]
```

## Notes

- **`CGO_ENABLED=0` is the load-bearing flag.** With cgo enabled Go links against libc dynamically, and the binary will not start on `scratch` or `distroless/static`. If a dependency genuinely needs cgo, use `distroless/base` instead.
- **`-ldflags="-s -w"`** strips the symbol table and DWARF debug info, typically 25–30% off the binary. Drop it when you need production stack traces with line numbers.
- **`distroless/static` over `scratch`** because it ships CA certificates, `/etc/passwd` with a `nonroot` user, and tzdata. On bare `scratch` you must copy certificates yourself:
  ```dockerfile
  COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
  ```
- **`USER 65532:65532`** is the numeric form of distroless's `nonroot`. A name won't resolve on an image with no user database.
- **Health checks** have no shell to run. Compile a subcommand into the binary and use `CMD ["/app", "healthcheck"]`, or let the orchestrator probe an HTTP endpoint.
- **Vendoring**: if the repo commits `vendor/`, drop the `go mod download` step and build with `-mod=vendor`. Otherwise keep `vendor/` in `.dockerignore`.
