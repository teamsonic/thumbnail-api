FROM python:3.12.6 AS build-stage

RUN pip install "poetry==1.8.3"
RUN python -m venv /venv

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY ["pyproject.toml", "poetry.lock", "/app/"]

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-dev --no-interaction

FROM python:3.12.6-slim-bookworm AS final

ARG APP_PORT
EXPOSE ${APP_PORT}

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

COPY --from=build-stage /venv /venv
COPY ["/app", "/app"]
COPY [ "log_conf.yaml", "/app/" ]

CMD [ "fastapi", "run", "srv" ]