FROM python:3.11-slim

# Set the working directory to the backend folder
WORKDIR /app/backend

# Copy requirements.txt from the project root
# We'll need to ensure requirements.txt is in the build context
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project from the build context into /app
COPY . /app

# Use PORT environment variable with a default of 8000
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Since the working directory is now /app/backend,
# use "main:app" (not "backend.main:app") for Uvicorn.
# Create a shell script to handle environment variable expansion
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && \
    chmod +x /app/start.sh

# Use JSON array format with the shell script
CMD ["/app/start.sh"]
