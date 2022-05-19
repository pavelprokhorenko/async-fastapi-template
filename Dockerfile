FROM python:3.9

ENV PATH="${PATH}:/root/.poetry/bin"

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - && \
    poetry config virtualenvs.create false
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install --no-interaction --no-dev --no-root --no-ansi -vvv


ENV PYTHONPATH=/app

WORKDIR /app

COPY . .
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN chmod +x ./docker-entrypoint.sh && \
    ln -s ./docker-entrypoint.sh /

EXPOSE 8080

ENTRYPOINT ["sh", "./docker-entrypoint.sh" ]
