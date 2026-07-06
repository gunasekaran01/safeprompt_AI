# syntax=docker/dockerfile:1

# SafePrompt AI frontend — a two-stage build. The first stage compiles
# the Vite/React SPA; the second serves the compiled static files (and
# reverse-proxies /api/* to the backend container) with Nginx. Only the
# small Nginx runtime stage — not Node, not node_modules, not source —
# ends up in the final image.

# ---- Build stage ---------------------------------------------------------
FROM node:20-alpine AS build
WORKDIR /app

# Installed from the lockfile before copying the rest of the source, so
# this (slow) layer is only rebuilt when dependencies actually change.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite inlines every VITE_* variable into the compiled JS at *build*
# time, not runtime — so they have to be passed in here as build args
# rather than as normal `docker run -e` environment variables. See
# docker-compose.yml's `frontend.build.args` (sourced from a root-level
# .env — see /.env.example) for how these get set.
ARG VITE_API_BASE_URL=/api
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_SUPABASE_URL=$VITE_SUPABASE_URL \
    VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

RUN npm run build

# ---- Runtime stage --------------------------------------------------------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
