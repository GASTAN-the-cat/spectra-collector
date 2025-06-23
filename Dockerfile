FROM python:3.11-slim
WORKDIR /app

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the app code
COPY app.py .

CMD ["python", "app.py"]
