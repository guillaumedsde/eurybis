import logging
import os
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
            "--encode-threads=8",
            "--cpu-affinity",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )
    # FIXME: waiting on https://github.com/Kludex/uvicorn/pull/2445
    os.environ["LIDIS_SOCKET_PATH"] = str(config.lidis_socket_path)
    os.environ["PIPE_SIZE"] = str(config.pipe_size)
    LOGGER.info(
        "Starting HTTP server %s:%d", config.http_listen_host, config.http_listen_port
    )
    ThreadingHTTPServer(
        (config.http_listen_host, config.http_listen_port), SpliceHandler
    ).serve_forever()
