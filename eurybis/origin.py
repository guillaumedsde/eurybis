import functools
import logging
import socket
import subprocess
import sys
from http.server import ThreadingHTTPServer

from eurybis import utils
from eurybis.api import SpliceHandler
from eurybis.config import OriginEurybisConfiguration
from eurybis.utils import compute_pipe_size

LOGGER = logging.getLogger(__name__)


def origin_server(config: OriginEurybisConfiguration):
    config.lidis_socket_path.unlink(missing_ok=True)
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-send",
            f"--from-unix={config.lidis_socket_path}",
            f"--to={config.lidis_send_host}:{config.lidis_send_port}",
            f"--max-clients={config.lidi_max_clients}",
            "--encode-threads=5",
            f"--to-mtu={config.lidi_udp_mtu}",
            f"--batch={config.lidi_udp_batch_size}",
            "--flush",
            "--cpu-affinity",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )
    LOGGER.info(
        "Starting HTTP server %s:%d", config.http_listen_host, config.http_listen_port
    )

    request_handler_class = functools.partial(
        SpliceHandler,
        splice_pipe_size=compute_pipe_size(config.lidi_max_clients),
        lidis_socket_path=config.lidis_socket_path,
    )
    httpd = ThreadingHTTPServer(
        (config.http_listen_host, config.http_listen_port), request_handler_class
    )
    httpd.socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_RCVBUF,
        utils.compute_pipe_size(config.lidi_max_clients),
    )

    httpd.serve_forever()
