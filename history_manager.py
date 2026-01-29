"""History management for tracking file count trends over time."""

import json
import base64
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime, timedelta
from typing import Dict, Optional


HISTORY_FILENAME = 'history.json'
TIMEOUT = 30  # seconds


def get_github_session() -> requests.Session:
    """Create a requests session with retry policy for GitHub API."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "PUT", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def fetch_history_from_github(token: str, owner: str, repo: str) -> Dict:
    """
    Fetch existing history.json from GitHub repository.

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner
        repo: Repository name

    Returns:
        History dict with 'data' list, or empty structure if not found
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{HISTORY_FILENAME}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = get_github_session().get(url, headers=headers, timeout=TIMEOUT)

    if response.status_code == 200:
        content_b64 = response.json().get('content', '')
        content = base64.b64decode(content_b64).decode('utf-8')
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("Warning: Could not parse history.json, starting fresh")
            return {"data": []}
    else:
        print(f"No existing history found (status {response.status_code}), starting fresh")
        return {"data": []}


def append_to_history(history: Dict, date: str, total_files: int, total_folders: int) -> Dict:
    """
    Add today's data to history, replacing if date already exists.

    Args:
        history: Existing history dict
        date: Date string in YYYY-MM-DD format
        total_files: Total file count
        total_folders: Total folder count

    Returns:
        Updated history dict
    """
    # Remove existing entry for this date if present
    history['data'] = [
        entry for entry in history.get('data', [])
        if entry.get('date') != date
    ]

    # Add new entry
    history['data'].append({
        'date': date,
        'total_files': total_files,
        'total_folders': total_folders
    })

    # Sort by date
    history['data'].sort(key=lambda x: x['date'])

    return history


def trim_history(history: Dict, days: int = 14) -> Dict:
    """
    Keep only the last N days of history.

    Args:
        history: History dict
        days: Number of days to keep (default 14)

    Returns:
        Trimmed history dict
    """
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')

    history['data'] = [
        entry for entry in history.get('data', [])
        if entry.get('date', '') >= cutoff_date
    ]

    return history


def save_history_to_github(
    token: str,
    owner: str,
    repo: str,
    history: Dict,
    branch: str = "master"
) -> None:
    """
    Save history.json to GitHub repository.

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner
        repo: Repository name
        history: History dict to save
        branch: Branch to upload to
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{HISTORY_FILENAME}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Pretty-print JSON for readability
    content = json.dumps(history, indent=2)
    content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')

    # Check if file exists (need SHA for update)
    r = get_github_session().get(url, headers=headers, timeout=TIMEOUT)
    existing_sha = r.json().get('sha') if r.status_code == 200 else None

    data = {
        "message": "Update history data",
        "content": content_b64,
        "branch": branch
    }

    if existing_sha:
        data["sha"] = existing_sha

    response = get_github_session().put(url, headers=headers, json=data, timeout=TIMEOUT)

    if response.status_code not in [200, 201]:
        raise Exception(f"GitHub API error saving history: {response.status_code} - {response.text}")

    print(f"History saved to GitHub ({len(history.get('data', []))} entries)")


def get_change_from_yesterday(history: Dict) -> Optional[int]:
    """
    Calculate the change in file count from yesterday.

    Args:
        history: History dict

    Returns:
        Change in files (negative = reduction), or None if not enough data
    """
    data = history.get('data', [])
    if len(data) < 2:
        return None

    # Data is sorted by date, get last two entries
    today_files = data[-1].get('total_files', 0)
    yesterday_files = data[-2].get('total_files', 0)

    return today_files - yesterday_files
