FROM python:3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Add --trusted-host pypi.org --trusted-host files.pythonhosted.org
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

COPY src/ .

COPY test/ .

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
