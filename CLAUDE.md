# Dropbox Folder Counter

## Overview

A Python tool that scans Dropbox folders recursively, counts files per subfolder, and generates an interactive HTML report with 14-day trend tracking. Reports are hosted via GitHub Pages.

**Live report:** https://joelcharlebois-ss.github.io/dropbox-report/

## Tech Stack

- **Language:** Python 3.11
- **APIs:** Dropbox SDK (`dropbox`), GitHub REST API (`requests`)
- **Visualization:** Chart.js (trend graph), Tabulator (sortable table)
- **Deployment:** GitHub Actions (scheduled), Google Cloud Functions (optional)
- **Hosting:** GitHub Pages

## Project Structure

```
dropbox-folder-counter/
├── main.py                 # Entry point, orchestrates pipeline
├── dropbox_scanner.py      # Dropbox API - BFS folder traversal
├── html_generator.py       # HTML report with Chart.js + Tabulator
├── history_manager.py      # 14-day sliding window persistence
├── github_uploader.py      # GitHub API for Pages deployment
├── requirements.txt        # Python dependencies
└── .github/workflows/
    └── daily-report.yml    # Scheduled job (9 AM UTC) with inline Python
```

## Key Modules

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `main.py` | Pipeline orchestration | `main()` - Cloud Function entry point |
| `dropbox_scanner.py` | Folder scanning | `scan_dropbox_folder()` - BFS traversal with pagination |
| `html_generator.py` | Report generation | `generate_html_report()` - Creates full HTML document |
| `history_manager.py` | Trend data | `fetch/append/trim/save_history_*()` |
| `github_uploader.py` | Deployment | `upload_html_to_github()`, `enable_pages()` |

## Execution Flow

See `main.py:28-104` for the orchestration sequence:
1. Load environment config (`main.py:44-49`)
2. Fetch existing history from GitHub (`main.py:52-54`)
3. Scan Dropbox via BFS (`main.py:56-59`)
4. Update history with today's totals (`main.py:65-69`)
5. Generate HTML report with chart (`main.py:71-74`)
6. Upload index.html + history.json to GitHub (`main.py:76-89`)

## Commands

### Local Development
```bash
# Setup
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Run (requires .env file)
python main.py
```

### Required Environment Variables
```
DROPBOX_ACCESS_TOKEN    # Dropbox API token
DROPBOX_ROOT_PATH       # Folder to scan (optional, defaults to root)
GITHUB_TOKEN            # GitHub PAT with repo scope
GITHUB_OWNER            # GitHub username/org
GITHUB_REPO             # Target repository name
```

### GitHub Actions
- Runs automatically at 9:00 AM UTC daily
- Manual trigger: Actions tab > "Daily Dropbox Report" > "Run workflow"

## Data Structures

### Folder Scan Result (`dropbox_scanner.py:54-57`)
```python
{'path': '/folder/name', 'file_count': 42}
# file_count = -1 indicates scan error
```

### History Entry (`history_manager.py:66-70`)
```python
{'date': 'YYYY-MM-DD', 'total_files': int, 'total_folders': int}
```

## Output Files (uploaded to GitHub)

- `index.html` - Interactive report with trend chart and searchable table
- `history.json` - Last 14 days of scan data

## Additional Documentation

When working on specific areas, consult these files:

| Topic | File |
|-------|------|
| Architectural patterns & design decisions | `.claude/docs/architectural_patterns.md` |
| Setup & troubleshooting | `README.md` |
