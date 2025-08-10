# Base image (Python 3.10)
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port 8000 (Django default)
EXPOSE 8000

# Run Django (adjust if using Gunicorn/etc.)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]