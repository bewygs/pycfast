FROM ubuntu:24.04 AS cfast-builder

ARG CFAST_TAG=CFAST-7.7.5
ARG CFAST_BUILD_DIR=gnu_linux_64
ARG CFAST_BUILD_SCRIPT=make_cfast.sh
ARG CFAST_BINARY_NAME=cfast7_linux_64

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gfortran \
    make \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${CFAST_TAG} https://github.com/firemodels/cfast.git /cfast-src

WORKDIR /cfast-src/Build/CFAST/${CFAST_BUILD_DIR}

RUN chmod +x ${CFAST_BUILD_SCRIPT} && ./${CFAST_BUILD_SCRIPT}

RUN cp ${CFAST_BINARY_NAME} /usr/local/bin/cfast && \
    chmod +x /usr/local/bin/cfast

FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=cfast-builder /usr/local/bin/cfast /usr/local/bin/cfast

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml README.md ./

COPY ./src ./src

RUN uv pip install --system --no-cache .

RUN cfast || true

CMD ["python"]