"""Cloud Function entry point for Dropbox Folder Counter."""

import os
import json
from datetime import datetime
import functions_framework
from flask import Request

from dropbox_scanner import scan_dropbox_folder
from html_generator import generate_html_report
from github_uploader import upload_html_to_github, check_pages_enabled, enable_pages
from history_manager import (
    fetch_history_from_github,
    append_to_history,
    trim_history,
    save_history_to_github
)


def get_env_var(name: str, required: bool = True) -> str:
    """Get environment variable with optional requirement check."""
    value = os.environ.get(name, '')
    if required and not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


@functions_framework.http
def main(request: Request):
    """
    HTTP Cloud Function entry point.

    Orchestrates:
    1. Fetching history from GitHub
    2. Scanning Dropbox folder for file counts
    3. Updating history with today's data
    4. Generating HTML report with trend chart
    5. Uploading to GitHub Pages

    Returns:
        JSON response with status and details
    """
    try:
        # Load configuration from environment
        dropbox_token = get_env_var('DROPBOX_ACCESS_TOKEN')
        dropbox_refresh_token = get_env_var('DROPBOX_REFRESH_TOKEN', required=False) or None
        dropbox_app_key = get_env_var('DROPBOX_APP_KEY', required=False) or None
        dropbox_app_secret = get_env_var('DROPBOX_APP_SECRET', required=False) or None
        dropbox_root = get_env_var('DROPBOX_ROOT_PATH', required=False) or ''
        github_token = get_env_var('GITHUB_TOKEN')
        github_owner = get_env_var('GITHUB_OWNER')
        github_repo = get_env_var('GITHUB_REPO')

        # Step 1: Fetch existing history
        print("Fetching history from GitHub...")
        history = fetch_history_from_github(github_token, github_owner, github_repo)
        print(f"Loaded {len(history.get('data', []))} history entries")

        # Step 2: Scan Dropbox
        print(f"Scanning Dropbox folder: {dropbox_root or '/'}")
        folder_data = scan_dropbox_folder(
            dropbox_token,
            dropbox_root,
            refresh_token=dropbox_refresh_token,
            app_key=dropbox_app_key,
            app_secret=dropbox_app_secret
        )
        print(f"Found {len(folder_data)} folders")

        # Calculate totals
        total_files = sum(f['file_count'] for f in folder_data if f['file_count'] >= 0)
        total_folders = len(folder_data)

        # Step 3: Update history with today's data
        today = datetime.utcnow().strftime('%Y-%m-%d')
        history = append_to_history(history, today, total_files, total_folders)
        history = trim_history(history, days=14)
        print(f"History now has {len(history.get('data', []))} entries")

        # Step 4: Generate HTML report with history for chart
        print("Generating HTML report with trend chart")
        html_content = generate_html_report(folder_data, dropbox_root, history)
        print(f"Generated HTML report ({len(html_content)} bytes)")

        # Step 5: Upload both files to GitHub
        print(f"Uploading to GitHub: {github_owner}/{github_repo}")

        # Upload HTML
        filename, pages_url = upload_html_to_github(
            github_token,
            github_owner,
            github_repo,
            html_content
        )
        print(f"Uploaded file: {filename}")

        # Upload history
        save_history_to_github(github_token, github_owner, github_repo, history)

        # Check/enable GitHub Pages
        if not check_pages_enabled(github_token, github_owner, github_repo):
            print("Enabling GitHub Pages...")
            enable_pages(github_token, github_owner, github_repo)

        # Return success response
        return json.dumps({
            'status': 'success',
            'folders_scanned': len(folder_data),
            'total_files': total_files,
            'history_entries': len(history.get('data', [])),
            'filename': filename,
            'pages_url': pages_url
        }), 200, {'Content-Type': 'application/json'}

    except ValueError as e:
        # Configuration error
        print(f"Configuration error: {e}")
        return json.dumps({
            'status': 'error',
            'error_type': 'configuration',
            'message': 'Invalid or missing configuration. Check server logs for details.'
        }), 400, {'Content-Type': 'application/json'}

    except Exception as e:
        # General error
        print(f"Error: {e}")
        return json.dumps({
            'status': 'error',
            'error_type': 'runtime',
            'message': 'An unexpected error occurred. Check server logs for details.'
        }), 500, {'Content-Type': 'application/json'}


# For local testing
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # Create a mock request
    class MockRequest:
        pass

    result, status_code, headers = main(MockRequest())
    print(f"Status: {status_code}")
    print(f"Response: {result}")
