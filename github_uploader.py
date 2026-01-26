"""GitHub Pages upload logic for hosting HTML reports."""

import base64
import requests
from typing import Tuple, Optional


REPORT_FILENAME = 'index.html'  # index.html for GitHub Pages root


def get_file_sha(token: str, owner: str, repo: str, path: str) -> Optional[str]:
    """
    Get the SHA of an existing file (needed for updates).

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner
        repo: Repository name
        path: File path in repo

    Returns:
        File SHA if exists, None otherwise
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('sha')
    return None


def upload_html_to_github(
    token: str,
    owner: str,
    repo: str,
    html_content: str,
    filename: str = REPORT_FILENAME,
    branch: str = "main"
) -> Tuple[str, str]:
    """
    Upload HTML content to GitHub repository.

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner (username or org)
        repo: Repository name
        html_content: HTML content to upload
        filename: Name for the file (default: index.html)
        branch: Branch to upload to

    Returns:
        Tuple of (filename, github_pages_url)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Encode content as base64
    content_b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')

    # Check if file exists (need SHA for update)
    existing_sha = get_file_sha(token, owner, repo, filename)

    data = {
        "message": "Update Dropbox folder report",
        "content": content_b64,
        "branch": branch
    }

    if existing_sha:
        data["sha"] = existing_sha

    response = requests.put(url, headers=headers, json=data)

    if response.status_code not in [200, 201]:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    # Generate GitHub Pages URL
    # Format: https://<owner>.github.io/<repo>/ for index.html
    # Format: https://<owner>.github.io/<repo>/<filename> for other files
    if filename == "index.html":
        pages_url = f"https://{owner}.github.io/{repo}/"
    else:
        pages_url = f"https://{owner}.github.io/{repo}/{filename}"

    return filename, pages_url


def check_pages_enabled(token: str, owner: str, repo: str) -> bool:
    """
    Check if GitHub Pages is enabled for the repository.

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner
        repo: Repository name

    Returns:
        True if Pages is enabled
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    return response.status_code == 200


def enable_pages(token: str, owner: str, repo: str, branch: str = "main") -> None:
    """
    Enable GitHub Pages for the repository.

    Args:
        token: GitHub Personal Access Token
        owner: Repository owner
        repo: Repository name
        branch: Branch to serve from
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "source": {
            "branch": branch,
            "path": "/"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code not in [201, 409]:  # 409 = already enabled
        print(f"Warning: Could not enable Pages: {response.status_code} - {response.text}")
