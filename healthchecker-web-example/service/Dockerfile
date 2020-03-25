FROM python:3.8
RUN mkdir /app
WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml /app/
RUN poetry install -n --no-root --no-dev
COPY healthchecker /app/healthchecker
COPY .flaskenv /app/.flaskenv
