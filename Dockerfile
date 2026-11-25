FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY app/ ./app/

EXPOSE 8000
# CMD убран — задаётся в docker-compose.yml