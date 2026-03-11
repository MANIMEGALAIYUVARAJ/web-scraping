# Stage 1: Build frontend
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: NGINX
FROM nginx:alpine

# 🔥 COPY YOUR NGINX CONFIG
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend build
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
