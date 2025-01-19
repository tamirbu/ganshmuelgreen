FROM python:3.8.20-alpine

WORKDIR /app

COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt
COPY builder.sh /app/builder.sh

RUN pip install -r requirements.txt
RUN apk add --no-cache docker
RUN apk add --no-cache docker-cli
RUN apk add git


VOLUME [ "/app/.git" ]

EXPOSE 5000

ENTRYPOINT [ "python", "main.py" ]
