FROM ghcr.io/astral-sh/uv:latest AS uv

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
COPY --from=uv /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY alembic.ini ./
COPY alembic ./alembic
COPY pravburo_ref_common ./pravburo_ref_common
CMD ["uv", "run", "--no-sync", "alembic", "upgrade", "head"]
