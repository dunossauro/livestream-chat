FROM python:3.10-slim
ENV POETRY_VIRTUALENVS_CREATE=false

COPY . .

RUN pip install poetry
RUN poetry install
EXPOSE 8000
CMD [ "uvicorn", "--host", "0.0.0.0", "app.app:app" ]
