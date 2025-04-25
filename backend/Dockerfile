# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY ./api ./api
COPY ./functions ./functions
COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
