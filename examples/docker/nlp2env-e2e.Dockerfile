# Reusable nlp2env image for examples/*/*/docker-compose.yml builds.
# Build context must be the nlp2env repository root.

FROM python:3.12-slim

WORKDIR /opt/nlp2env

COPY pyproject.toml README.md LICENSE ./
COPY src ./src/
COPY examples/lib ./examples/lib/
COPY examples/write ./examples/write/
COPY examples/integrators ./examples/integrators/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[mcp]"

ARG CACHE_BUST=0
RUN echo "$CACHE_BUST" > /tmp/.cache-bust

ARG E2E_SCRIPT=examples/write/smtp-email/e2e.sh
ENV E2E_SCRIPT=${E2E_SCRIPT}
ENV NLP2ENV_ROOT=/opt/nlp2env
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

WORKDIR /workspace
ENTRYPOINT []
CMD ["/bin/bash", "-euo", "pipefail", "-c", "bash /opt/nlp2env/${E2E_SCRIPT}"]
