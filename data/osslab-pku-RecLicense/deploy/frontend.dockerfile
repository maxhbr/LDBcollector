FROM node:16 AS builder

# install dependencies
RUN mkdir /frontend
COPY ./frontend/package-lock.json ./frontend/package.json /frontend/
WORKDIR /frontend
RUN npm ci --force

# Build frontend
ARG NODE_ENV
ARG REACT_APP_BASE_URL
COPY ./frontend/ /frontend
RUN npm run build

FROM caddy

EXPOSE 80
EXPOSE 443
# Copy caddy configration
COPY deploy/frontend.caddyfile /etc/caddy/Caddyfile
# Copy artifact
COPY --from=builder /frontend/dist /wwwroot