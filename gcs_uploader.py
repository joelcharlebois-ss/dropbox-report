"""Google Cloud Storage upload logic for hosting HTML reports."""

from pathlib import Path
from typing import Tuple

from google.cloud import storage
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/devstorage.read_write']
REPORT_FILENAME = 'dropbox_folder_report.html'
TOKEN_FILE = Path(__file__).parent / 'token_gcs.json'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'


def get_credentials():
    """
    Get OAuth credentials for Google Cloud Storage.

    On first run, opens browser for authentication.
    Subsequent runs use saved refresh token.

    Returns:
        Google OAuth credentials
    """
    creds = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If no valid credentials, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"OAuth credentials file not found: {CREDENTIALS_FILE}\n"
                    "Download it from Google Cloud Console:\n"
                    "1. Go to https://console.cloud.google.com/apis/credentials\n"
                    "2. Create OAuth 2.0 Client ID (Desktop app)\n"
                    "3. Download JSON and save as 'credentials.json'"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def upload_html_to_gcs(
    bucket_name: str,
    html_content: str,
    filename: str = REPORT_FILENAME
) -> Tuple[str, str]:
    """
    Upload HTML content to Google Cloud Storage.

    Args:
        bucket_name: GCS bucket name
        html_content: HTML content to upload
        filename: Name for the file

    Returns:
        Tuple of (blob_name, public_url)
    """
    creds = get_credentials()
    client = storage.Client(credentials=creds)

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(filename)

    # Upload with HTML content type
    blob.upload_from_string(
        html_content,
        content_type='text/html'
    )

    # Generate public URL
    public_url = f"https://storage.googleapis.com/{bucket_name}/{filename}"

    return filename, public_url


def create_bucket_if_not_exists(bucket_name: str, project_id: str, location: str = "US") -> None:
    """
    Create a GCS bucket if it doesn't exist.

    Args:
        bucket_name: Name for the bucket
        project_id: GCP project ID
        location: Bucket location
    """
    creds = get_credentials()
    client = storage.Client(credentials=creds, project=project_id)

    try:
        bucket = client.get_bucket(bucket_name)
        print(f"Bucket {bucket_name} already exists")
    except Exception:
        bucket = client.create_bucket(bucket_name, location=location)
        print(f"Created bucket {bucket_name}")

    # Make bucket publicly readable
    bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    bucket.patch()

    # Set public read policy
    policy = bucket.get_iam_policy(requested_policy_version=3)
    policy.bindings.append({
        "role": "roles/storage.objectViewer",
        "members": ["allUsers"]
    })
    bucket.set_iam_policy(policy)
    print(f"Bucket {bucket_name} is now publicly readable")
