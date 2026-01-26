"""One-time setup script to create and configure GCS bucket."""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/devstorage.full_control']
TOKEN_FILE = Path(__file__).parent / 'token_gcs.json'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'
PROJECT_ID = 'teranet-dropbox-summary'


def get_credentials():
    """Get OAuth credentials for Google Cloud Storage."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def setup_bucket(bucket_name: str):
    """Create bucket and make it publicly readable."""
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=PROJECT_ID)

    # Check if bucket exists
    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket '{bucket_name}' already exists")
    except Exception as e:
        print(f"Creating bucket '{bucket_name}'...")
        bucket = client.create_bucket(bucket_name, location="US")
        print(f"Created bucket '{bucket_name}'")

    # Make bucket publicly readable
    print("Setting public access...")
    policy = bucket.get_iam_policy(requested_policy_version=3)

    # Add public read access
    policy.bindings.append({
        "role": "roles/storage.objectViewer",
        "members": ["allUsers"]
    })
    bucket.set_iam_policy(policy)

    print(f"\nBucket setup complete!")
    print(f"Your reports will be accessible at:")
    print(f"  https://storage.googleapis.com/{bucket_name}/dropbox_folder_report.html")


if __name__ == '__main__':
    load_dotenv()
    bucket_name = os.environ.get('GCS_BUCKET_NAME', 'teranet-dropbox-reports')
    setup_bucket(bucket_name)
