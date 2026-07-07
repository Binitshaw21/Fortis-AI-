# Use a lightweight Python base
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (for psycopg2)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy requirements and install (bypassing cache limits)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Django code
COPY . .

# Move into backend directory where manage.py is located
WORKDIR /app/backend

# Run migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Default port for local / Hugging Face (Railway overrides this dynamically)
ENV PORT=7860
EXPOSE $PORT

# Change the shell form to allow variable expansion
CMD gunicorn fortis_project.wsgi:application --bind 0.0.0.0:$PORT

