FROM python:3.11.7-slim
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install poetry
COPY . .
RUN poetry install
EXPOSE 8000
CMD [ "poetry", "run", "uvicorn", "--host", "0.0.0.0", "app.app:app" ]
