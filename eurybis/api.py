import fcntl
import os
import pathlib
import socket
from http.server import BaseHTTPRequestHandler


class SpliceHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/":
            self.send_error(404)
            return

        content_length = self.headers.get("Content-Length")
        if not content_length:
            self.send_error(411, "Content-Length required")
            return

        remaining = int(content_length)

        # Open Unix domain socket connection per request
        uds = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        uds.connect(os.environ["LIDIS_SOCKET_PATH"])

        client_fd = self.connection.fileno()
        uds_fd = uds.fileno()

        buffered_bytes = bytearray(self.rfile.peek())
        remaining -= uds.send(buffered_bytes)

        pipe_r, pipe_w = os.pipe()
        os.set_blocking(pipe_r, False)
        os.set_blocking(pipe_w, False)
        size = int(pathlib.Path("/proc/sys/fs/pipe-max-size").read_text())
        fcntl.fcntl(pipe_w, fcntl.F_SETPIPE_SZ, size)
        fcntl.fcntl(pipe_r, fcntl.F_SETPIPE_SZ, size)

        try:
            while remaining > 0:
                chunk = min(size, remaining)

                # socket -> pipe
                moved_in = os.splice(client_fd, pipe_w, chunk)
                if moved_in == 0:
                    break

                # pipe -> unix socket
                sent = os.splice(pipe_r, uds_fd, moved_in)
                if sent == 0:
                    raise RuntimeError("splice to UDS returned 0")

                remaining -= moved_in

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK\n")

        except Exception as e:
            self.send_error(500, str(e))

        finally:
            os.close(pipe_r)
            os.close(pipe_w)
            uds.close()

    def log_message(self, format, *args):
        return  # silence logging
