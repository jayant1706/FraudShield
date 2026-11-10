# ==============================================================================
# FraudShield Production Frontend Dockerfile
# Multi-stage build for React TypeScript Vite Dashboard + Nginx Reverse Proxy
# ==============================================================================

# Stage 1: Build React Assets
FROM node:22-alpine AS build

WORKDIR /app

# Copy dependency manifests
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Nginx Alpine
FROM nginx:1.27-alpine AS runtime

# Copy build artifacts to Nginx html directory
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

