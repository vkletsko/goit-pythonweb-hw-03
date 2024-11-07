FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN /root/.local/bin/poetry install --no-root

COPY . .

EXPOSE ${PORT:-3000}

CMD ["python", "main.py"]
