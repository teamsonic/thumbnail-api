FROM python:3.12.6 as build-stage
RUN pip install "poetry==1.8.3"

RUN python -m venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY ["pyproject.toml", "poetry.lock", "/app/"]
RUN poetry install --no-dev --no-interaction

FROM python:3.12.6-slim-bookworm as final

ARG APP_PORT
EXPOSE ${APP_PORT}

ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
WORKDIR /app

COPY --from=build-stage /venv /venv
COPY ["/app", "/app"]

CMD [ "fastapi", "run", "cmd" ]