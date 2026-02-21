import datetime
import os
import pathlib


def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


class BandwidthCounter:
    def __enter__(self):
        self._start = datetime.datetime.now()
        self.byte_count = 0
        self._end = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._end = datetime.datetime.now()

    @property
    def bandwidth(self) -> float | None:
        if not self._start:
            return None
        now = self._end if self._end else datetime.datetime.now()
        return self.byte_count / (now - self._start).total_seconds()

    @property
    def hf_bandwidth(self) -> str:
        return sizeof_fmt(self.bandwidth, suffix="B/s")


def compute_pipe_size(max_pipe_count: int) -> int:
    page_size = os.sysconf("SC_PAGE_SIZE")
    pipe_max_size = int(pathlib.Path("/proc/sys/fs/pipe-max-size").read_text())
    pipe_user_pages_soft = int(
        pathlib.Path("/proc/sys/fs/pipe-user-pages-soft").read_text()
    )
    pipe_user_pages_hard = int(
        pathlib.Path("/proc/sys/fs/pipe-user-pages-hard").read_text()
    )
    pipe_user_page_limit = pipe_user_pages_soft or pipe_user_pages_hard
    pipe_user_bytes_soft = pipe_user_page_limit * page_size

    # Select optimal size
    optimal_pipe_size_for_n_pipes = min(
        pipe_max_size, pipe_user_bytes_soft // max_pipe_count
    )

    clamped_optimal_pipe_size = (optimal_pipe_size_for_n_pipes // page_size) * page_size

    return max(page_size, clamped_optimal_pipe_size)
