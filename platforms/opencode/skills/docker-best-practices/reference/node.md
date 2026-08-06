# Node

Node needs its runtime in the final image, so the floor is the size of the base — roughly 80–200MB depending on variant. The win comes from keeping build tooling and dev dependencies out.

## Dockerfile

```dockerfile
# Stage 1: Build
FROM node:24-slim AS build
WORKDIR /app

# Dependencies resolve from the manifest alone, so this layer survives source edits.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Stage 2: Production dependencies only
FROM node:24-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 3: Production
FROM node:24-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
USER node
CMD ["node", "dist/index.js"]
```

## Notes

- **The separate `deps` stage** is what keeps dev dependencies out. Reusing the build stage's `node_modules` ships every test framework and bundler to production; re-resolving with `--omit=dev` usually halves the image.
- **`npm ci`, not `npm install`** — it installs from the lock file and fails when the lock and manifest disagree, which is the reproducibility a build wants.
- **`USER node`** works here: the official images already define a `node` user. Set it after the last `COPY`, since a non-root user can't write to a root-owned `WORKDIR`.
- **`ENV NODE_ENV=production`** changes framework behaviour at runtime and is easy to forget once the dependency pruning moved to its own stage.
- **Alpine** cuts roughly 100MB but ships musl instead of glibc. Native modules with prebuilt binaries (`sharp`, `better-sqlite3`, anything node-gyp) may fall back to compiling from source or fail outright. Prefer `slim` unless you've verified the dependency tree.
- **Keep `node_modules` in `.dockerignore`.** Copying a host-built tree into the image ships binaries compiled for the wrong platform.
