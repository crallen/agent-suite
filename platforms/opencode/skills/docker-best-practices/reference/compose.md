# Docker Compose

## Development

The goal is a fast edit-reload loop, so this is the one place mounting source is correct.

```yaml
services:
  app:
    build:
      context: .
      target: development      # a dev stage of the multi-stage build
    volumes:
      - .:/app                 # mount source for hot reload
      - deps:/app/node_modules # keep the container's deps, unmasked by the mount
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:18-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=devpassword
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 5

volumes:
  db-data:
  deps:
```

## Notes on the development file

- **The anonymous-volume trick** (`deps:/app/node_modules`) stops the bind mount at `/app` from hiding the dependencies installed inside the image. The same problem and fix applies to any ecosystem whose dependencies live under the project directory — `target/` for Rust, `.venv/` for Python. Languages that install dependencies outside the source tree, like Go's module cache, don't need it.
- **`condition: service_healthy`** is what makes `depends_on` mean "ready", not merely "started". Without a healthcheck on the dependency, the app starts against a database still initialising.
- **Compiled languages get less from source mounting**, since a rebuild is required anyway. A bind mount plus a file watcher that reruns `cargo run` or `go run` works, but is often slower than rebuilding the image; measure before assuming it helps.

## Production

- **Don't mount source.** Copy it into the image so the running artifact matches what was built and scanned.
- **Set `restart: unless-stopped`** for resilience.
- **Set memory and CPU limits**, so one container can't starve the host.
- **Set `read_only: true`** on the root filesystem, with `tmpfs` for paths that need writes.
- **Use named volumes** for persistent data, never bind mounts to host paths.
- **Don't expose unnecessary ports.** Inter-service traffic uses the Compose network and needs no `ports:` entry.
- **Pass secrets via `secrets:` or the environment at runtime**, never in the image or a committed `.env`.

```yaml
services:
  app:
    image: registry.example.com/app:1.4.2   # a pinned tag or digest, never latest
    restart: unless-stopped
    read_only: true
    tmpfs:
      - /tmp
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
```
