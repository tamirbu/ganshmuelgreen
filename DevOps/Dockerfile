FROM python:3.8.20-alpine

WORKDIR /app

COPY main.py /app/main.py
COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python", "main.py" ]