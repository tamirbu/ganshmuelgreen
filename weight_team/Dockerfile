FROM python:3.12-slim

WORKDIR /app

# Install only the minimum required packages
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

COPY weight_service.py .

EXPOSE 5000

CMD ["python", "weight_service.py"]
