# chimera-api-hp

A high-performance HTTP echo server built on [Axum](https://github.com/tokio-rs/axum) for **Web Application Firewall (WAF) throughput benchmarking and latency attribution**. Part of the [Chimera](https://github.com/atlas-crew/Chimera) WAF testing toolkit.

```bash
docker pull nickcrew/chimera-api-hp:latest
docker run --rm -p 8890:8890 nickcrew/chimera-api-hp
```

## What it does

Provides a near-zero-overhead HTTP endpoint that mirrors every incoming request back as JSON. Designed as a **baseline** for measuring WAF performance — any latency or throughput degradation you observe is attributable to the WAF, not the backend.

- **~500k requests/second** on a single modern core (echo workload)
- **9.8 MB** distroless image (`gcr.io/distroless/cc-debian12:nonroot`)
- **~2 MB** RAM at idle
- **Multi-arch**: `linux/amd64` + `linux/arm64`
- Built on Tokio's work-stealing async runtime

## Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `/healthz` | GET | Liveness probe — `{"status": "healthy"}` |
| `/echo` | ANY | Mirrors method, path, headers, query params, body as JSON |
| `/echo/{*rest}` | ANY | Same, with wildcard subpath capture |
| `/status/{code}` | GET | Returns the requested HTTP status code |

Add `?delay_ms=N` to any `/echo` request to inject simulated latency (capped at 5000ms) — useful for testing WAF timeout behavior.

## Quick example

```bash
# Start the server
docker run --rm -d --name echo -p 8890:8890 nickcrew/chimera-api-hp

# Echo a request
curl -X POST 'http://localhost:8890/echo?source=load-test' \
  -H 'Content-Type: application/json' \
  -d '{"payload": "hello"}'

# Response:
# {
#   "method": "POST",
#   "path": "/echo",
#   "query": {"source": "load-test"},
#   "headers": {...},
#   "body": {"payload": "hello"},
#   "body_size": 20,
#   "timestamp": "2026-04-12T04:51:08.556493+00:00"
# }

# Trigger arbitrary status codes
curl -i http://localhost:8890/status/418   # I'm a teapot

docker stop echo
```

## Configuration

Configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8890` | TCP port to bind |
| `RUST_LOG` | `info` | Log level (`error`, `warn`, `info`, `debug`, `trace`) |

## Tags

| Tag | Description |
|-----|-------------|
| `latest` | Most recent release |
| `0.1.1` | Specific version (semver patch) |
| `0.1` | Latest in 0.1.x line (semver minor) |
| `sha-<commit>` | Pinned to a specific git commit (immutable) |

For production use, **pin to a specific version or commit SHA** rather than `latest`.

## Use cases

- **WAF throughput benchmarking** — measure peak request rate with a backend that adds near-zero overhead, isolating WAF performance from application behavior
- **Latency attribution** — calculate WAF-induced latency by comparing direct vs WAF-routed request times against the same echo target
- **Integration testing** — deterministic HTTP mirror for client test suites and reverse proxy validation
- **Traffic capture sinks** — receive and inspect arbitrary HTTP traffic during load tests, contract tests, or gateway validation

## Security

Runs as a **non-root user** (UID 65532, distroless `nonroot`) with no shell, package manager, or writable filesystem outside `/tmp`. The image surface area is the Rust binary plus the minimal `cc-debian12` runtime.

## Source and license

- **Source**: https://github.com/atlas-crew/Chimera/tree/main/apps/vuln-api-hp
- **Crates.io**: https://crates.io/crates/chimera-api-hp
- **License**: MIT
- **Issues**: https://github.com/atlas-crew/Chimera/issues
