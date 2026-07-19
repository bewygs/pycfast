FROM ubuntu:24.04 AS cfast-builder

ARG CFAST_TAG=CFAST-7.7.7
ARG CFAST_BUILD_DIR=gnu_linux
ARG CFAST_BUILD_SCRIPT=make_cfast.sh
ARG CFAST_BINARY_NAME=cfast7_linux

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

FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=cfast-builder /usr/local/bin/cfast /usr/local/bin/cfast

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgfortran5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Builds the sdist from the local checkout. The package version is resolved
# by hatch-vcs from git tags, so this stage needs the full repo (including
# .git) with unabridged history — the CI checkout step must use
# fetch-depth: 0, or the version will fail to resolve.
FROM base AS sdist-builder

WORKDIR /src

COPY . .

RUN uv build --sdist --out-dir /dist

# Default target: install the package built from the local checkout above.
FROM base AS local

COPY --from=sdist-builder /dist /dist

RUN uv pip install --system --no-cache /dist/*.tar.gz

CMD ["python"]

# Release target: install the already-published PyPI release. No git
# history is needed here since the version is pinned explicitly.
FROM base AS pypi

ARG PYCFAST_VERSION

RUN test -n "$PYCFAST_VERSION" || \
    (echo "PYCFAST_VERSION build-arg is required for the 'pypi' target" >&2 && exit 1)

RUN uv pip install --system --no-cache "pycfast==${PYCFAST_VERSION}"

CMD ["python"]