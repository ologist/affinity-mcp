FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all source first (needed for local package install)
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY app.py ./

# Install project + dependencies
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser /app
USER appuser

CMD ["python", "app.py"]
