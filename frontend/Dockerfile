# syntax=docker/dockerfile:1

FROM node:20-alpine AS dev

RUN addgroup -g 1001 -S nodejs && adduser -S -u 1001 -G nodejs nodejs

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .
RUN chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 5173

CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM node:20-alpine AS build

RUN addgroup -g 1001 -S nodejs && adduser -S -u 1001 -G nodejs nodejs

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY --chown=nodejs:nodejs . .

USER nodejs

RUN pnpm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
