import os
import requests
import json
from supabase import create_client, Client

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

BUCKET_NAME = "uploads"

def upload_file_to_storage(file_content, file_path):
    """Upload a file to Supabase Storage"""
    try:
        # Upload file using the storage API
        response = supabase.storage.from_(BUCKET_NAME).upload(
            file_path,
            file_content
        )
        
        # Generate a URL path for the file
        file_url = f"supabase://{BUCKET_NAME}/{file_path}"
        return file_url
    except Exception as e:
        raise Exception(f"Supabase upload error: {str(e)}")

def download_file_from_storage(file_path, local_path):
    """Download a file from Supabase Storage to a local path"""
    try:
        # Get file content
        response = supabase.storage.from_(BUCKET_NAME).download(file_path)
        
        # Write to local file
        with open(local_path, "wb") as f:
            f.write(response)
            
        return local_path
    except Exception as e:
        raise Exception(f"Supabase download error: {str(e)}")

def get_file_url(file_path, expires_in=3600):
    """Generate a signed URL for a file"""
    try:
        # Create a signed URL
        signed_url = supabase.storage.from_(BUCKET_NAME).create_signed_url(
            file_path,
            expires_in
        )
        
        # Return the signed URL
        if isinstance(signed_url, dict) and "signedURL" in signed_url:
            return signed_url["signedURL"]
        return signed_url
    except Exception as e:
        # Fallback to public URL if signed URL fails
        try:
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
            return public_url
        except:
            raise Exception(f"Supabase URL generation error: {str(e)}")
