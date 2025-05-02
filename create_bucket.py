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
    "Authorization": f"Bearer {SUPABASE_KEY}",
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

# Now let's set up a policy to allow authenticated users to access the bucket
try:
    # Create a policy for authenticated users
    policy_response = requests.post(
        f"{SUPABASE_URL}/storage/v1/bucket/{BUCKET_NAME}/policy",
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
        print(f"Successfully created policy for bucket '{BUCKET_NAME}'!")
    else:
        print(f"Failed to create policy: {policy_response.status_code} - {policy_response.text}")
except Exception as e:
    print(f"Error creating policy: {str(e)}")
