FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-server-dev-all \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
