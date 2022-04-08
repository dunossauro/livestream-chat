FROM python:3.10
ENV POETRY_VIRTUALENVS_CREATE=false

COPY . .

RUN pip install poetry
RUN poetry install
EXPOSE 8000
CMD [ "uvicorn", "app.app:app" ]

# Comandos
# buildah bud -t youtube_chat .
# podman run -p 8000:8000 youtube_chat