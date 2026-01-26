"""Google Drive upload logic using OAuth user credentials."""

import json
import os
from io import BytesIO
from pathlib import Path
from typing import Optional, Tuple

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


SCOPES = ['https://www.googleapis.com/auth/drive.file']
REPORT_FILENAME = 'dropbox_folder_report.html'
TOKEN_FILE = Path(__file__).parent / 'token.json'
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'


def get_drive_service():
    """
    Create Google Drive service using OAuth user credentials.

    On first run, opens browser for authentication.
    Subsequent runs use saved refresh token.

    Returns:
        Google Drive service object
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

    return build('drive', 'v3', credentials=creds)


def find_existing_file(service, folder_id: str, filename: str) -> Optional[str]:
    """
    Find an existing file by name in a folder.

    Args:
        service: Google Drive service object
        folder_id: ID of the folder to search in
        filename: Name of the file to find

    Returns:
        File ID if found, None otherwise
    """
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)'
    ).execute()

    files = results.get('files', [])

    if files:
        return files[0]['id']

    return None


def upload_html_to_drive(
    folder_id: str,
    html_content: str,
    filename: str = REPORT_FILENAME
) -> Tuple[str, str]:
    """
    Upload HTML content to Google Drive, overwriting if exists.

    Args:
        folder_id: Target Google Drive folder ID
        html_content: HTML content to upload
        filename: Name for the file

    Returns:
        Tuple of (file_id, web_view_link)
    """
    service = get_drive_service()

    # Check if file already exists
    existing_file_id = find_existing_file(service, folder_id, filename)

    # Prepare the media
    media = MediaIoBaseUpload(
        BytesIO(html_content.encode('utf-8')),
        mimetype='text/html',
        resumable=True
    )

    if existing_file_id:
        # Update existing file
        file = service.files().update(
            fileId=existing_file_id,
            media_body=media
        ).execute()
        file_id = existing_file_id
    else:
        # Create new file
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/html'
        }

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        file_id = file.get('id')

    # Get the web view link
    file_info = service.files().get(
        fileId=file_id,
        fields='webViewLink'
    ).execute()

    web_view_link = file_info.get('webViewLink', f'https://drive.google.com/file/d/{file_id}/view')

    return file_id, web_view_link


def set_file_public(file_id: str) -> None:
    """
    Make a file publicly accessible via link.

    Args:
        file_id: ID of the file to make public
    """
    service = get_drive_service()

    permission = {
        'type': 'anyone',
        'role': 'reader'
    }

    service.permissions().create(
        fileId=file_id,
        body=permission
    ).execute()
