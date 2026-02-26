# 🪉 Eurybis

Eurybis is a proof-of-concept implementation of a webserver for receiving data to send through a unidirectional network link.
Files are sent through the unidirectional link using [ANSSI-FR/lidi](https://github.com/ANSSI-FR/lidi) and are stored on disk at destination.

The goal of the PoC is to implement high performance transfer of files received by the HTTP server, this repository does so using:
- Zero-copy transfer from the HTTP server's socket to lidi's socket
- A free-threaded python build
- `asyncio` whenever possible on the destination side
- The `ThreadingHTTPServer` in the Python standard library on the origin side
- TODO: [kTLS](https://docs.kernel.org/networking/tls-offload.html)?

## 🏁 Requirements

- docker
- docker compose
- Linux kernel >= 4.5

## 🚀 How to use?

```bash
docker compose up --build --wait
# Send 2GB to the HTTP API
head --bytes $((2 * 1024 * 1024 * 1024)) /dev/urandom | curl \
    --request POST \
    --data-binary @- \
    http://localhost:8080/
```
