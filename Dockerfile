FROM python:3.13-slim

WORKDIR /lms

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . .

RUN mkdir -p /lms/media
RUN mkdir -p /lms/static

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]