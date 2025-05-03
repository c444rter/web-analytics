import os
import requests
import json
import time

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uploads")

# Headers for Supabase API requests (using anon key by default)
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# Headers for admin operations (using service role key)
admin_headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

def upload_file_to_storage(file_content, file_path, use_admin=False):
    """Upload a file to Supabase Storage using REST API
    
    Args:
        file_content: The content of the file to upload
        file_path: The path where the file will be stored
        use_admin: Whether to use admin permissions (service role key)
    """
    try:
        # Construct the upload URL
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_path}"
        
        # Choose headers based on permission level needed
        request_headers = admin_headers if use_admin else headers
        
        # Upload the file
        response = requests.post(
            upload_url,
            headers=request_headers,
            data=file_content
        )
        
        # Check if the upload was successful
        if response.status_code not in (200, 201):
            raise Exception(f"Upload failed with status {response.status_code}: {response.text}")
        
        # Generate a URL path for the file
        file_url = f"supabase://{BUCKET_NAME}/{file_path}"
        return file_url
    except Exception as e:
        raise Exception(f"Supabase upload error: {str(e)}")

def download_file_from_storage(file_path, local_path, use_admin=False):
    """Download a file from Supabase Storage to a local path using REST API
    
    Args:
        file_path: The path of the file in storage
        local_path: The local path to save the file to
        use_admin: Whether to use admin permissions (service role key)
    """
    try:
        # Construct the download URL
        download_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_path}"
        
        # Choose headers based on permission level needed
        request_headers = admin_headers if use_admin else headers
        
        # Download the file
        response = requests.get(
            download_url,
            headers=request_headers
        )
        
        # Check if the download was successful
        if response.status_code != 200:
            raise Exception(f"Download failed with status {response.status_code}: {response.text}")
        
        # Write to local file
        with open(local_path, "wb") as f:
            f.write(response.content)
            
        return local_path
    except Exception as e:
        raise Exception(f"Supabase download error: {str(e)}")

def get_file_url(file_path, expires_in=3600, use_admin=False):
    """Generate a signed URL for a file using REST API
    
    Args:
        file_path: The path of the file in storage
        expires_in: The expiration time in seconds
        use_admin: Whether to use admin permissions (service role key)
    """
    try:
        # Construct the signed URL endpoint
        signed_url_endpoint = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET_NAME}/{file_path}"
        
        # Choose headers based on permission level needed
        request_headers = admin_headers if use_admin else headers
        
        # Request a signed URL
        response = requests.post(
            signed_url_endpoint,
            headers=request_headers,
            json={"expiresIn": expires_in}
        )
        
        # Check if the request was successful
        if response.status_code != 200:
            # Fallback to public URL
            return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_path}"
        
        # Return the signed URL
        result = response.json()
        if "signedURL" in result:
            return result["signedURL"]
        
        # Fallback to public URL
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_path}"
    except Exception as e:
        # Fallback to public URL if signed URL fails
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_path}"

def admin_create_bucket(bucket_name, public=False, file_size_limit=52428800):
    """Create a new storage bucket (requires service role key)
    
    Args:
        bucket_name: The name of the bucket to create
        public: Whether the bucket should be public
        file_size_limit: Maximum file size in bytes (default 50MB)
    """
    if not SUPABASE_SERVICE_ROLE_KEY:
        raise Exception("SUPABASE_SERVICE_ROLE_KEY is not set. Cannot perform admin operations.")
        
    try:
        # Construct the bucket creation URL
        bucket_url = f"{SUPABASE_URL}/storage/v1/bucket"
        
        # Create the bucket
        response = requests.post(
            bucket_url,
            headers=admin_headers,
            json={
                "name": bucket_name,
                "public": public,
                "file_size_limit": file_size_limit
            }
        )
        
        # Check if the creation was successful
        if response.status_code not in (200, 201):
            raise Exception(f"Bucket creation failed with status {response.status_code}: {response.text}")
        
        return response.json()
    except Exception as e:
        raise Exception(f"Supabase bucket creation error: {str(e)}")
