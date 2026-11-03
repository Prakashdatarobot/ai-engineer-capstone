FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    CSV_PATH=/data/dataset-tickets-multi-lang-4-20k.csv \
    JSON_PATH=/data/tickets.json \
    LIMIT=100

WORKDIR /app

# Dependencies first so this layer is cached when only code changes
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-install-project

COPY README.md ./
COPY src ./src
COPY tests ./tests
RUN uv sync --locked

# Fail the build if any test fails
RUN uv run --no-sync pytest -q -p no:cacheprovider

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser
USER appuser

CMD ["tta-capstone-project"]
