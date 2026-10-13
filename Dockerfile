FROM oven/bun:1-debian

WORKDIR /app

COPY package.json ./
RUN bun install --no-cache

COPY . .

ENV NODE_ENV=production
EXPOSE 3000

USER bun
CMD ["bun", "run", "server.ts"]
