# 1) Choose a base image with Python
FROM python:3.10

# 2) Set a working directory in the container
WORKDIR /app

# 3) Copy your requirements.txt into the container
COPY requirements.txt .

# 4) Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy the rest of your code into the container
COPY . .

# 6) Expose the FastAPI port (default 8000)
EXPOSE 8000

# 7) Default command to run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
