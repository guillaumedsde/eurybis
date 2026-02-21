import datetime


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
