FROM docker.io/library/golang:1.24-alpine AS build

WORKDIR /src
COPY src/go.mod ./
COPY src/*.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -trimpath -ldflags="-s -w" -o /out/bibliotheca .

FROM docker.io/library/alpine:3.22

RUN adduser -D -H -u 10001 app
USER app
COPY --from=build /out/bibliotheca /bibliotheca
EXPOSE 8080
ENTRYPOINT ["/bibliotheca"]
