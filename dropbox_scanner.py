"""Dropbox folder scanning logic."""

import dropbox
from dropbox.files import FolderMetadata, FileMetadata
from collections import deque
from typing import List, Dict, Any, Optional


def scan_dropbox_folder(
    access_token: str,
    root_path: str,
    refresh_token: Optional[str] = None,
    app_key: Optional[str] = None,
    app_secret: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Recursively scan a Dropbox folder and count direct files in each subfolder.

    Args:
        access_token: Dropbox API access token
        root_path: Root folder path to scan (e.g., "/MyFolder" or "" for root)
        refresh_token: OAuth2 refresh token for automatic token refresh
        app_key: Dropbox app key (required with refresh_token)
        app_secret: Dropbox app secret (optional, for confidential apps)

    Returns:
        List of dictionaries with 'path' and 'file_count' keys
    """
    if refresh_token and app_key:
        dbx = dropbox.Dropbox(
            oauth2_access_token=access_token,
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret
        )
    else:
        dbx = dropbox.Dropbox(access_token)
    results: List[Dict[str, Any]] = []

    # Normalize root path (empty string for root, otherwise ensure leading slash)
    if root_path and not root_path.startswith('/'):
        root_path = '/' + root_path
    if root_path == '/':
        root_path = ''

    # Queue of folders to process
    folders_to_scan = deque([root_path])

    while folders_to_scan:
        current_path = folders_to_scan.popleft()
        file_count = 0

        try:
            # List folder contents with pagination
            result = dbx.files_list_folder(current_path)
            entries = result.entries

            while result.has_more:
                result = dbx.files_list_folder_continue(result.cursor)
                entries.extend(result.entries)

            # Process entries
            for entry in entries:
                if isinstance(entry, FileMetadata):
                    file_count += 1
                elif isinstance(entry, FolderMetadata):
                    # Add subfolder to scan queue
                    folders_to_scan.append(entry.path_lower)

            # Record this folder's direct file count
            display_path = current_path if current_path else '/'
            results.append({
                'path': display_path,
                'file_count': file_count
            })

        except dropbox.exceptions.ApiError as e:
            print(f"Error scanning {current_path}: {e}")
            # Still record the folder with -1 to indicate error
            display_path = current_path if current_path else '/'
            results.append({
                'path': display_path,
                'file_count': -1,
                'error': str(e)
            })

    # Sort results by path for consistent output
    results.sort(key=lambda x: x['path'].lower())

    return results
