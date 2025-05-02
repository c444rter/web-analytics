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

# Try to update the bucket to be public
try:
    update_response = requests.put(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}",
        headers=headers,
        json={
            "public": True,
            "file_size_limit": 52428800  # 50MB limit
        }
    )

    if update_response.status_code in (200, 201, 204):
        print(f"Successfully updated bucket '{BUCKET_NAME}' to be public!")
    else:
        print(f"Failed to update bucket: {update_response.status_code} - {update_response.text}")
except Exception as e:
    print(f"Error updating bucket: {str(e)}")

# Try different policy endpoints
policy_endpoints = [
    f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}/policy",
    f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}/policies",
    f"{SUPABASE_URL}/storage/v1/policies"
]

for endpoint in policy_endpoints:
    try:
        print(f"Trying policy endpoint: {endpoint}")
        
        # Create a policy for anonymous users to read
        anon_policy_response = requests.post(
            endpoint,
            headers=headers,
            json={
                "name": "Allow anonymous reads",
                "bucket_id": BUCKET_NAME,
                "definition": {
                    "role": "anon",
                    "operations": ["SELECT"]
                }
            }
        )

        if anon_policy_response.status_code in (200, 201, 204):
            print(f"Successfully created anonymous read policy for bucket '{BUCKET_NAME}'!")
            break
        else:
            print(f"Failed with endpoint {endpoint}: {anon_policy_response.status_code} - {anon_policy_response.text}")
    except Exception as e:
        print(f"Error with endpoint {endpoint}: {str(e)}")
