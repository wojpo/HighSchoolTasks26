FROM oven/bun:1

WORKDIR /app

RUN chown -R bun:bun /app

COPY --chown=bun:bun src/package.json src/bun.lock ./

USER bun

RUN bun install --frozen-lockfile

COPY --chown=bun:bun src/ .

RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "preview"]