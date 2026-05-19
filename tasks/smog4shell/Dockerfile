FROM oven/bun:1

WORKDIR /app

COPY src .

RUN bun install --frozen-lockfile

RUN bun run build

CMD bun run start