FROM python:3.11-slim

# Set the working directory to the backend folder
WORKDIR /app/backend

# Copy requirements.txt from the project root
# We'll need to ensure requirements.txt is in the build context
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project from the build context into /app
COPY . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

# IMPORTANT: Do NOT run migrations here
# Migrations are completely bypassed for this deployment
# since the database tables already exist

# Since the working directory is now /app/backend,
# use "main:app" (not "backend.main:app") for Uvicorn.
# Use a hardcoded port for Railway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
