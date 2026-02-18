import fcntl
import os
import socket
from http.server import BaseHTTPRequestHandler


class SpliceHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.spice_pipe_size = int(os.environ["PIPE_SIZE"])
        self.lidis_socket_path = os.environ["LIDIS_SOCKET_PATH"]
        return super().__init__(request, client_address, server)

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
        uds.connect(self.lidis_socket_path)

        client_fd = self.connection.fileno()
        uds_fd = uds.fileno()

        pipe_r, pipe_w = os.pipe()
        fcntl.fcntl(pipe_w, fcntl.F_SETPIPE_SZ, self.spice_pipe_size)
        fcntl.fcntl(pipe_r, fcntl.F_SETPIPE_SZ, self.spice_pipe_size)

        try:
            buffered = self.rfile.read1(remaining)
            print("initial buffer", buffered)
            uds.sendall(buffered)
            remaining -= len(buffered)

            while remaining > 0:
                chunk = min(self.spice_pipe_size, remaining)

                # socket -> pipe
                moved_in = os.splice(client_fd, pipe_w, chunk)
                if moved_in == 0:
                    break

                # pipe -> unix socket
                sent = os.splice(pipe_r, uds_fd, moved_in)
                if sent == 0:
                    raise RuntimeError("splice to UDS returned 0")
                if sent != moved_in:
                    raise RuntimeError("Partial pipe splice")
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
