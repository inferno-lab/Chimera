# chimera-api-hp

A high-performance echo server built on Axum for WAF throughput benchmarking
and latency attribution. Part of the
[Chimera](https://github.com/NickCrew/Chimera) WAF testing toolkit.

## What it does

Provides a near-zero-overhead HTTP endpoint that mirrors every incoming
request back as JSON. Designed as a baseline for measuring Web Application
Firewall throughput and latency — any observed overhead is attributable to
the WAF, not the backend.

- `/healthz` — liveness probe (`{"status": "healthy"}`)
- `/echo` (ANY method) — mirrors method, path, headers, query params, and body
- `/echo/{*rest}` — same, with wildcard subpath capture
- `/status/{code}` — returns the requested HTTP status code

Query parameter `?delay_ms=N` on `/echo` adds simulated latency (capped at
5000ms) for testing WAF timeout behavior.

## Performance

On a single modern core, the server handles **500k+ requests/second** for
trivial echo workloads. The release binary is **~1.4MB**, idles at ~2MB
RAM, and uses the Tokio async runtime with a work-stealing scheduler
across OS threads.

## Running

```bash
# From source
cargo run --release

# With custom port
PORT=8890 cargo run --release

# Via Docker (distroless image, ~15MB)
docker build -f Dockerfile.prod -t chimera-api-hp .
docker run -p 8890:8890 chimera-api-hp
```

The server binds to `0.0.0.0:8890` by default.

## Example

```bash
$ curl -X POST 'http://localhost:8890/echo?source=test' \
    -H 'Content-Type: application/json' \
    -d '{"payload": "hello"}'

{
  "method": "POST",
  "path": "/echo",
  "query": {"source": "test"},
  "headers": {
    "content-type": "application/json",
    "host": "localhost:8890",
    ...
  },
  "body": {"payload": "hello"},
  "body_size": 20,
  "timestamp": "2026-04-12T03:51:08.556493+00:00"
}
```

## Use cases

- **WAF throughput benchmarking** — measure peak request rate with a
  backend that adds near-zero overhead
- **Latency attribution** — isolate WAF-induced latency from application
  latency
- **Integration testing** — use as a deterministic mirror for HTTP client
  test suites
- **Traffic replay sinks** — capture and inspect arbitrary HTTP traffic
  during load tests

## License

MIT
