# Dockerfile

FROM python:3.10-bullseye

# copy source and install dependencies
ENV VIRTUAL_ENV=/venv
RUN python3.10 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONPATH=/app

WORKDIR /app

COPY . .
COPY docker-entrypoint.sh ./docker-entrypoint.sh
COPY requirements.txt ./requirements.txt
RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev && \
    chmod +x ./docker-entrypoint.sh && \
    ln -s ./docker-entrypoint.sh /

RUN pip install -r ./requirements.txt

# start service
STOPSIGNAL SIGTERM
CMD ["sh", "docker-entrypoint.sh"]
