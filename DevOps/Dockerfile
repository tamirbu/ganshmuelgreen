FROM python:3.8.20-alpine

ENV DOCKER_COMPOSE_VERSION=2.23.0

WORKDIR /app

COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt
COPY builder.sh /app/builder.sh

RUN apk add --no-cache \
      curl \
      docker \
      py3-pip \
      libffi-dev \
      py3-cryptography \
      py3-cffi \
      make \
      gcc \
      musl-dev && \
      git && \
    curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose && \
    pip install -r requirements.txt && \
    chmod +x /usr/local/bin/docker-compose && \
    chmod +x builder.sh

ENTRYPOINT [ "python", "main.py" ]
