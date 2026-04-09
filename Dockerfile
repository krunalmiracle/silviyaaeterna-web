FROM oven/bun:1-debian

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git config --global user.email "ai@inspector.local" && \
    git config --global user.name "AI Inspector"

COPY . .

RUN bun install

EXPOSE 3000

CMD ["bun", "run", "server.ts"]
