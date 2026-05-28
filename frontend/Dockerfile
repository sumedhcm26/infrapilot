# ============================================================
# InfraPilot Frontend Dockerfile
# Multi-stage build: build with Node, serve with nginx
# ============================================================

# Stage 1: Build the React app
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (Docker layer caching optimization)
COPY package*.json ./
RUN npm ci --silent

# Copy source and build
COPY . .

# Pass the backend URL as a build argument
# Override with: docker build --build-arg VITE_API_URL=https://your-backend.render.com
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve with nginx (tiny, production-grade static server)
FROM nginx:alpine AS runtime

# Copy built files to nginx's default web root
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config to handle React Router (SPA routing)
# Without this, refreshing on /services would return 404
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
