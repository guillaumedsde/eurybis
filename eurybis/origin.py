import logging
import os
import subprocess
import sys

import uvicorn

from eurybis.api import app
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
            "--flush",
            "--encode-threads=6",
            "--cpu-affinity",
        ),
        stderr=sys.stderr,
        stdout=sys.stdout,
    )
    # FIXME: waiting on https://github.com/Kludex/uvicorn/pull/2445
    os.environ["LIDIS_SOCKET_PATH"] = str(config.lidis_socket_path)
    uvicorn.run(
        app,
        host=config.http_listen_host,
        port=config.http_listen_port,
        log_level=logging.getLevelNamesMapping()[config.log_level],
        http="httptools",
        loop="uvloop",
    )
