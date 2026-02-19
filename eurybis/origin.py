import functools
import logging
import subprocess
import sys
from http.server import ThreadingHTTPServer

from eurybis.api import SpliceHandler
from eurybis.config import OriginEurybisConfiguration

LOGGER = logging.getLogger(__name__)


def origin_server(config: OriginEurybisConfiguration):
    config.lidis_socket_path.unlink(missing_ok=True)
    LOGGER.info("Starting lidi")
    subprocess.Popen(
        (
            "diode-send",
            f"--from-unix={config.lidis_socket_path}",
            f"--to={config.lidis_send_host}:{config.lidis_send_port}",
            f"--max-clients={config.lidis_max_clients}",
            # "--flush",
            "--encode-threads=5",
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
        splice_pipe_size=config.pipe_size,
        lidis_socket_path=config.lidis_socket_path,
    )
    ThreadingHTTPServer(
        (config.http_listen_host, config.http_listen_port), request_handler_class
    ).serve_forever()
