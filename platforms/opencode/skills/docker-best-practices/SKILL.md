---
name: docker-best-practices
description: Docker image design — the static-binary vs runtime base-image decision, multi-stage builds, layer caching, security hardening, and Compose patterns. Load when writing or reviewing a Dockerfile or Compose file, or shrinking an image.
---

# Docker Best Practices

Build images that are small, cache well, and carry no more attack surface than the process needs.

The judgment lives here; the concrete Dockerfiles live in `reference/`. Read the file for the project's stack:

| Reference | Contents |
|---|---|
| `docker-best-practices/reference/go.md` | Static binary → `scratch` / distroless, numeric UID |
| `docker-best-practices/reference/rust.md` | `cargo-chef` dependency caching → distroless |
| `docker-best-practices/reference/node.md` | Runtime image, dependency-manifest-first caching |
| `docker-best-practices/reference/compose.md` | Development and production Compose patterns |

Working in a stack with no file above? Settle the base-image decision below, then follow the closest reference file — the one that shares its answer, not its syntax.

## The Base-Image Decision

Everything else follows from one question: **does the built artifact need a runtime, or is it a self-contained binary?**

| Artifact | Final base | Typical size | Why |
|---|---|---|---|
| Static binary (Go, Rust, Zig, C) | `scratch`, or `gcr.io/distroless/static` | 10–30MB | No shell, no package manager, no libc CVEs to patch |
| Dynamically linked binary | `gcr.io/distroless/base` or `*-slim` | 30–80MB | Needs libc and certificates, nothing more |
| Needs a language runtime (Node, Python, Ruby, JVM) | `*-slim`, or `*-alpine` where the ecosystem tolerates musl | 80–250MB | The interpreter or VM must ship with the app |

Reaching for `*-slim` when the language emits a static binary is the most common miss — it costs an order of magnitude in size and leaves a userland you now have to patch.

Two consequences for the static-binary case that catch people out:

- **`scratch` has no `/etc/passwd`**, so `USER appuser` fails. Use a numeric UID (`USER 65532:65532`) — distroless images already define `nonroot` at 65532.
- **`scratch` has no CA certificates**, so outbound TLS fails. Copy them from the build stage, or use `distroless/static`, which includes them.

Always pin the base to a specific version. Never `latest` in production.

## Multi-Stage Builds

Separate build dependencies from the runtime image. The final stage should contain only what the process needs to run — never a compiler, package manager, or test tooling.

This matters most where the build toolchain is large relative to the artifact: a Rust or Go toolchain is hundreds of megabytes producing a binary of tens.

## Layer Caching

Docker caches layers top-down, so order them by how often they change:

1. Base image — rarely
2. System packages — infrequently
3. **Dependencies, resolved from the manifest alone** — when dependencies change
4. Application source — most often

Step 3 is the one that pays. Copy only the dependency manifest, resolve dependencies, *then* copy source — so editing a source file doesn't re-resolve the dependency graph. Every ecosystem has a form of this, and the compiled languages need a trick to achieve it because their dependency and source builds are one command; the stack files show each.

## Reduce Image Size

- Use `--no-install-recommends` with `apt-get`.
- Clean package manager caches in the same `RUN` layer: `rm -rf /var/lib/apt/lists/*`.
- Keep a `.dockerignore` (see below) — it shrinks the build context and stops local artifacts leaking into the image.
- Never install development or test dependencies in the production stage.
- Combine related `RUN` commands to reduce layers.

## Security Hardening

- **Run as non-root.** Create a user in the runtime stage, or use a numeric UID where the base has no user database.
- **Never bake secrets into the image.** Layers persist even when a later layer deletes the file. Use build secrets (`RUN --mount=type=secret,...`) for private registries.
- **Set a read-only root filesystem** at runtime, via Compose or the orchestrator.

**Security checklist:**
- [ ] Runs as non-root user
- [ ] No secrets baked into the image, including in deleted layers
- [ ] Base image is pinned and regularly updated
- [ ] Only necessary ports are exposed
- [ ] No unnecessary capabilities (drop all, add specific)
- [ ] `.dockerignore` excludes sensitive files (.env, .git, credentials)
- [ ] Final stage contains no compiler, package manager, or shell it doesn't need

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1
```

A `scratch` or distroless image has no `curl` and no shell. Either build a health endpoint the orchestrator probes directly (Kubernetes `httpGet`), or compile a tiny health subcommand into the binary itself and use `CMD ["/app", "healthcheck"]`.

## .dockerignore

Start from this and add the project's build output and dependency directories:

```
.git
.gitignore
Dockerfile*
docker-compose*
.dockerignore
.env
.env.*
*.md
LICENSE
.vscode
.idea
coverage
```

Then add what the stack generates locally and must not enter the image — `node_modules` for Node, `target/` for Rust, `__pycache__` for Python, `vendor/` for Go when not vendoring deliberately.
