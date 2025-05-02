import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase configuration from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uploads")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY environment variables are not set.")
    print("Please set them in your .env file.")
    exit(1)

print(f"Using SUPABASE_URL: {SUPABASE_URL}")
print(f"Using BUCKET_NAME: {BUCKET_NAME}")

# Headers for Supabase API requests
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# Check if we can connect to Supabase
try:
    # Try to list buckets
    response = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers
    )
    
    if response.status_code == 200:
        buckets = response.json()
        print(f"Successfully connected to Supabase Storage!")
        print(f"Available buckets: {[bucket['name'] for bucket in buckets]}")
        
        # Check if our bucket exists
        if any(bucket['name'] == BUCKET_NAME for bucket in buckets):
            print(f"Bucket '{BUCKET_NAME}' exists!")
        else:
            print(f"Bucket '{BUCKET_NAME}' does not exist. You may need to create it.")
    else:
        print(f"Failed to connect to Supabase Storage: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error connecting to Supabase: {str(e)}")

# Try to connect to the database
print("\nTrying to connect to the database...")
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set.")
    exit(1)

print(f"Using DATABASE_URL: {DATABASE_URL}")

try:
    # Try to parse the connection string
    parts = DATABASE_URL.split("@")[1].split("/")[0].split(":")
    host = parts[0]
    port = parts[1]
    
    print(f"Trying to connect to host: {host} on port: {port}")
    
    # Try to ping the host
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    result = s.connect_ex((host, int(port)))
    if result == 0:
        print(f"Successfully connected to {host}:{port}!")
    else:
        print(f"Failed to connect to {host}:{port}. Error code: {result}")
    s.close()
except Exception as e:
    print(f"Error parsing or connecting to database: {str(e)}")
