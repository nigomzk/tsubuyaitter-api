FROM python:3.13-slim-bookworm

# enviroment settings.
ENV LANG=C.UTF-8
ENV TZ=Asia/Tokyoche/uv
# 仮想環境を作成せずにパッケージをインストール
ENV UV_PROJECT_ENVIRONMENT=/usr/local
# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1
# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /uvx /bin/

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

# working directory settings.
WORKDIR /app/

COPY ./pyproject.toml ./uv.lock /app/
COPY ./app /app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync

CMD ["uvicorn", "app.main:app", "--reload", "--host=0.0.0.0", "--port=5000"]