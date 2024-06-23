FROM python:3.12.4-slim
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry
COPY pyproject.toml poetry.lock .
RUN poetry install --no-root

COPY . .
EXPOSE 9000
CMD poetry run uvicorn --host 0.0.0.0 --port 9000 app.app:app
