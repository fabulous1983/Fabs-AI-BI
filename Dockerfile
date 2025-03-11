FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev odbcinst curl gnupg2

WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "server:app"]
