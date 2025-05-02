import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase configuration from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpcGRhaW5sYXNma2tnd3hvZXhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjEyMzAzMCwiZXhwIjoyMDYxNjk5MDMwfQ.MQO_oVqtFCJYLzoF8SxH8zgLKMkxGdFz2N3H9CnpJ9E"

if not SUPABASE_URL:
    print("ERROR: SUPABASE_URL environment variable is not set.")
    print("Please set it in your .env file.")
    exit(1)

print(f"Using SUPABASE_URL: {SUPABASE_URL}")
print(f"Using SERVICE_ROLE_KEY for authentication")

# Headers for Supabase API requests with service role key
headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# List all buckets
try:
    response = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers
    )

    if response.status_code == 200:
        buckets = response.json()
        print(f"Successfully retrieved buckets!")
        print(f"Number of buckets: {len(buckets)}")
        for bucket in buckets:
            print(f"Bucket: {bucket.get('name')} (Public: {bucket.get('public')})")
    else:
        print(f"Failed to retrieve buckets: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error retrieving buckets: {str(e)}")
