FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev odbcinst curl gnupg2

# Install Microsoft ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Set working directory inside the container
WORKDIR /app

# Copy all files from the current directory into the container
COPY . .

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt

# Command to run when the container starts
CMD ["python", "server.py"]
