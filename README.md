# Dropbox Folder File Counter

A Python tool that scans a Dropbox folder recursively, counts files in each subfolder, and generates an interactive HTML report hosted on GitHub Pages. Includes a 14-day progress chart to track file count trends over time.

## Features

- Recursively scans all subfolders in a Dropbox directory
- Counts direct files per folder (not recursive totals)
- Generates interactive HTML report with sortable, searchable table
- **14-day progress chart** showing file count trends
- **"Change from yesterday"** indicator to track daily progress
- Hosted on GitHub Pages for easy access
- Runs daily via GitHub Actions (9:00 AM UTC)
- Supports OAuth2 refresh tokens for long-running automation

## Live Report

View the report at: https://joelcharlebois-ss.github.io/dropbox-report/

## Project Structure

```
dropbox-folder-counter/
├── .github/
│   └── workflows/
│       └── daily-report.yml    # GitHub Actions workflow
├── main.py                     # Entry point (Cloud Function compatible)
├── dropbox_scanner.py          # Dropbox API logic
├── html_generator.py           # HTML report generation with Chart.js
├── history_manager.py          # Historical data management
├── github_uploader.py          # GitHub Pages upload logic
├── get_refresh_token.py        # OAuth2 helper to obtain refresh tokens
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## How It Works

1. **GitHub Actions** triggers the workflow daily at 9:00 AM UTC
2. **Dropbox API** scans the configured folder and counts files
3. **History manager** fetches previous data and appends today's count
4. **HTML generator** creates the report with Chart.js trend graph
5. **GitHub API** uploads `index.html` and `history.json` to the repo
6. **GitHub Pages** serves the report publicly

## Setup Instructions

### 1. Dropbox API Setup

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access" and "Full Dropbox"
4. Name your app and create it
5. Under "Permissions", enable:
   - `files.metadata.read`
6. Under "Settings", note your **App key** and **App secret**

#### Obtaining OAuth2 Tokens

Short-lived access tokens expire after 4 hours. For automated daily runs, you need a refresh token:

1. Add your App key and App secret to `.env`:
   ```
   DROPBOX_APP_KEY=your_app_key
   DROPBOX_APP_SECRET=your_app_secret
   ```
2. Run the helper script:
   ```bash
   python get_refresh_token.py
   ```
3. Authorize the app in your browser when prompted
4. Copy the tokens output and add them to your secrets/`.env`

### 2. GitHub Repository Setup

1. Create a new GitHub repository (or use existing)
2. Push this code to the repository
3. Enable GitHub Pages:
   - Go to Settings → Pages
   - Set source to the `master` branch, root folder

### 3. Configure GitHub Secrets

Go to your repository's **Settings → Secrets and variables → Actions** and add:

| Secret Name | Required | Description |
|-------------|----------|-------------|
| `DROPBOX_ACCESS_TOKEN` | Yes | Dropbox OAuth2 access token |
| `DROPBOX_REFRESH_TOKEN` | Yes | Dropbox OAuth2 refresh token (for auto-renewal) |
| `DROPBOX_APP_KEY` | Yes | Dropbox app key (for token refresh) |
| `DROPBOX_APP_SECRET` | No | Dropbox app secret (for confidential apps) |
| `DROPBOX_ROOT_PATH` | No | Folder path to scan (e.g., `/My Folder/subfolder`) |
| `GH_PAT` | Yes | GitHub Personal Access Token with `repo` scope |

#### Creating a GitHub Personal Access Token

1. Go to [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select the `repo` scope
4. Copy the token and add it as `GH_PAT` secret

### 4. Test the Workflow

1. Go to **Actions** tab in your repository
2. Select "Daily Dropbox Report"
3. Click "Run workflow" → "Run workflow"
4. Check the report at `https://<username>.github.io/<repo>/`

## Local Development

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file with your credentials:
   ```
   DROPBOX_ACCESS_TOKEN=your_access_token
   DROPBOX_REFRESH_TOKEN=your_refresh_token
   DROPBOX_APP_KEY=your_app_key
   DROPBOX_APP_SECRET=your_app_secret
   DROPBOX_ROOT_PATH=/path/to/scan
   GITHUB_TOKEN=your_github_pat
   GITHUB_OWNER=your_username
   GITHUB_REPO=your_repo
   ```
5. Run locally:
   ```bash
   python main.py
   ```

## HTML Report Features

- **14-day trend chart**: Visual progress toward your file reduction goal
- **Change indicator**: Shows daily file count change (green ↓ = reduction, red ↑ = increase)
- **Sortable columns**: Click column headers to sort
- **Search**: Filter folders by path
- **Pagination**: Navigate large folder lists
- **Statistics**: Total folder and file counts

## Troubleshooting

### Viewing Logs

**GitHub Actions:**
- Go to your repository → Actions tab → Select workflow run → Click job → View step output

**Google Cloud Functions** (if deployed):
- Google Cloud Console → Cloud Functions → Select function → "Logs" tab
- Or via CLI: `gcloud functions logs read <function-name>`

**Local development:**
- Logs print directly to the terminal when running `python main.py`

### "Dropbox path not found"
- Verify the `DROPBOX_ROOT_PATH` secret uses spaces, not URL encoding
- Example: `/Quebec Project/pendingInbox` (correct) vs `/Quebec%20Project/pendingInbox` (wrong)

### "Token expired" or authentication errors
- Ensure you have set up refresh tokens (see OAuth2 setup above)
- Verify `DROPBOX_REFRESH_TOKEN` and `DROPBOX_APP_KEY` secrets are configured
- Run `get_refresh_token.py` to obtain new tokens if needed

### "Branch not found" error
- Ensure the workflow is configured for your default branch (`master` or `main`)
- Check the `branch` parameter in the workflow file

### Workflow not appearing
- Make a small commit to the workflow file to trigger detection
- Check the Actions tab is enabled for your repository

## License

MIT License
