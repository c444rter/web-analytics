import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase configuration from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpcGRhaW5sYXNma2tnd3hvZXhtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjEyMzAzMCwiZXhwIjoyMDYxNjk5MDMwfQ.MQO_oVqtFCJYLzoF8SxH8zgLKMkxGdFz2N3H9CnpJ9E"
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uploads")

if not SUPABASE_URL:
    print("ERROR: SUPABASE_URL environment variable is not set.")
    print("Please set it in your .env file.")
    exit(1)

print(f"Using SUPABASE_URL: {SUPABASE_URL}")
print(f"Using BUCKET_NAME: {BUCKET_NAME}")
print(f"Using SERVICE_ROLE_KEY for authentication")

# Headers for Supabase API requests with service role key
headers = {
    "apikey": SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
    "Content-Type": "application/json"
}

# Create the bucket
try:
    # Try to create the bucket
    response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers,
        json={
            "name": BUCKET_NAME,
            "public": False,
            "file_size_limit": 52428800  # 50MB limit
        }
    )

    if response.status_code in (200, 201):
        print(f"Successfully created bucket '{BUCKET_NAME}'!")
    else:
        print(f"Failed to create bucket: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error creating bucket: {str(e)}")

# Now let's set up policies to allow authenticated users to access the bucket
try:
    # Create a policy for authenticated users
    policy_response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}/policies",
        headers=headers,
        json={
            "name": "Allow authenticated uploads",
            "definition": {
                "role": "authenticated",
                "operations": ["SELECT", "INSERT", "UPDATE", "DELETE"]
            }
        }
    )

    if policy_response.status_code in (200, 201):
        print(f"Successfully created authenticated policy for bucket '{BUCKET_NAME}'!")
    else:
        print(f"Failed to create authenticated policy: {policy_response.status_code} - {policy_response.text}")
        
    # Create a policy for anonymous users to read
    anon_policy_response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}/policies",
        headers=headers,
        json={
            "name": "Allow anonymous reads",
            "definition": {
                "role": "anon",
                "operations": ["SELECT"]
            }
        }
    )

    if anon_policy_response.status_code in (200, 201):
        print(f"Successfully created anonymous read policy for bucket '{BUCKET_NAME}'!")
    else:
        print(f"Failed to create anonymous policy: {anon_policy_response.status_code} - {anon_policy_response.text}")
except Exception as e:
    print(f"Error creating policy: {str(e)}")
