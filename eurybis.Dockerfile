
FROM ghcr.io/astral-sh/uv:trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_LOCKED=1 \
    UV_NO_EDITABLE=1 \
    UV_PYTHON_INSTALL_DIR=/python \
    UV_PYTHON_PREFERENCE=only-managed

RUN --mount=type=bind,source=.python-version,target=.python-version \
    uv python install "$(cat .python-version)"

WORKDIR /eurybis
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project
COPY . /eurybis
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

FROM gcr.io/distroless/cc:nonroot AS base

WORKDIR /eurybis

# Copy the python interpreter from the builder
COPY --from=builder --chown=nonroot:nonroot /python /python

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /eurybis /eurybis

# Place executables in the environment at the front of the path
ENV PATH="/eurybis/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER nonroot

FROM base AS receiver

VOLUME [ "/data" ]

EXPOSE 6000

ENTRYPOINT ["python", "/eurybis/eurybis/receiver.py"]
CMD [ "/data" ]


FROM base AS origin

EXPOSE 8080

ENTRYPOINT ["python", "/eurybis/eurybis/origin_http_server.py"]
