# NOTE: use Google's "distroless with libgcc1" base image, see:
#       https://github.com/GoogleContainerTools/distroless/blob/6755e21ccd99ddead6edc8106ba03888cbeed41a/cc/README.md
ARG BASE_IMAGE_FINAL_STAGES="gcr.io/distroless/cc:nonroot"

FROM rust:1.93-trixie AS builder

USER nobody

WORKDIR /lidi

ADD https://github.com/ANSSI-FR/lidi.git#v2.1.1 .

RUN cargo build --release --bin diode-send --bin diode-receive

FROM ${BASE_IMAGE_FINAL_STAGES} AS send

COPY --from=builder --chown=root:root --chmod=755 /lidi/target/release/diode-send /usr/local/bin/
ENTRYPOINT ["diode-send"]

FROM ${BASE_IMAGE_FINAL_STAGES} AS receive

COPY --from=builder --chown=root:root --chmod=755 /lidi/target/release/diode-receive /usr/local/bin/
ENTRYPOINT ["diode-receive"]
