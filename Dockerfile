FROM python:3.12-slim-bookworm
RUN apt update && apt install -y libpq-dev gcc
RUN pip install -U pip poetry==1.8.4
WORKDIR /app
COPY --from=ghcr.io/ufoscout/docker-compose-wait:latest /wait /wait
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry lock && poetry install
COPY ./ ./
ENTRYPOINT ["sh", "/app/startup.sh"]