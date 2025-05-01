import os
import requests
import json
import time

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uploads")

# Headers for Supabase API requests
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def upload_file_to_storage(file_content, file_path):
    """Upload a file to Supabase Storage using REST API"""
    try:
        # Construct the upload URL
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_path}"
        
        # Upload the file
        response = requests.post(
            upload_url,
            headers=headers,
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

def download_file_from_storage(file_path, local_path):
    """Download a file from Supabase Storage to a local path using REST API"""
    try:
        # Construct the download URL
        download_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_path}"
        
        # Download the file
        response = requests.get(
            download_url,
            headers=headers
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

def get_file_url(file_path, expires_in=3600):
    """Generate a signed URL for a file using REST API"""
    try:
        # Construct the signed URL endpoint
        signed_url_endpoint = f"{SUPABASE_URL}/storage/v1/object/sign/{BUCKET_NAME}/{file_path}"
        
        # Request a signed URL
        response = requests.post(
            signed_url_endpoint,
            headers=headers,
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
