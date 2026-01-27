# Architectural Patterns

This document describes recurring patterns and design decisions in the codebase.

## Module Separation

Each concern is isolated into its own module with a single responsibility:

| Module | Responsibility |
|--------|----------------|
| `dropbox_scanner.py` | External API integration (Dropbox) |
| `html_generator.py` | Presentation layer (HTML/JS) |
| `history_manager.py` | Data persistence (history) |
| `github_uploader.py` | External API integration (GitHub) |
| `main.py` | Orchestration only |

**References:**
- `main.py:9-17` - Clean imports showing module boundaries
- Each module exposes 1-3 public functions with clear interfaces

## Pipeline Orchestration

`main.py` follows a linear pipeline pattern where each step feeds into the next:

```
fetch_history → scan_dropbox → update_history → generate_html → upload
```

**Reference:** `main.py:51-89`

The orchestrator:
- Contains no business logic itself
- Handles only configuration loading and error handling
- Logs progress between steps

## GitHub as Backend

Instead of a traditional database, the system uses GitHub for:

1. **Data persistence** - `history.json` stored in repo via Contents API
2. **Static hosting** - `index.html` served via GitHub Pages
3. **Scheduling** - GitHub Actions cron trigger

**References:**
- `history_manager.py:13-43` - Fetch via Contents API with base64 decode
- `history_manager.py:99-144` - Save via PUT with SHA for updates
- `github_uploader.py:37-93` - Same pattern for HTML upload

**Pattern:** Check for existing file SHA before PUT to handle create vs update:
- `github_uploader.py:68-69`
- `history_manager.py:126-128`

## BFS Folder Traversal

`dropbox_scanner.py` uses breadth-first search with a queue to traverse folders:

**Reference:** `dropbox_scanner.py:28-50`

```python
folders_to_scan = [root_path]
while folders_to_scan:
    current_path = folders_to_scan.pop(0)
    # ... process folder ...
    for entry in entries:
        if isinstance(entry, FolderMetadata):
            folders_to_scan.append(entry.path_lower)
```

Benefits:
- Memory-efficient (no recursion stack)
- Natural pagination support
- Easy to add rate limiting if needed

## Pagination Handling

Dropbox API returns paginated results. The scanner handles this with cursor-based continuation:

**Reference:** `dropbox_scanner.py:36-42`

```python
result = dbx.files_list_folder(current_path)
entries = result.entries
while result.has_more:
    result = dbx.files_list_folder_continue(result.cursor)
    entries.extend(result.entries)
```

## Graceful Degradation

Errors don't crash the entire scan. Failed folders are recorded with a sentinel value:

**Reference:** `dropbox_scanner.py:59-67`

- `file_count = -1` indicates an error
- Error message stored in optional `error` field
- HTML generator displays "Error" in red for these entries (`html_generator.py:44-47`)

## Path Privacy

Root path is stripped from display paths to avoid exposing full folder structure:

**Reference:** `html_generator.py:34-41`

```python
if root_path and path.lower().startswith(root_path.lower()):
    display_path = path[len(root_path):]
```

## Sliding Window History

History is capped at 14 days to keep the dataset manageable:

**Reference:** `history_manager.py:78-96`

```python
def trim_history(history: Dict, days: int = 14) -> Dict:
    cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    history['data'] = [
        entry for entry in history.get('data', [])
        if entry.get('date', '') >= cutoff_date
    ]
```

## Idempotent Updates

Same-day scans replace rather than duplicate entries:

**Reference:** `history_manager.py:59-63`

```python
history['data'] = [
    entry for entry in history.get('data', [])
    if entry.get('date') != date
]
```

This allows re-running the scan multiple times per day safely.

## Environment-Based Configuration

All secrets and configuration come from environment variables:

**Reference:** `main.py:20-25, 44-49`

Benefits:
- Works in Cloud Functions, GitHub Actions, and local dev
- No hardcoded credentials
- `.env` file support for local development (`main.py:127-128`)

## Dual Deployment Strategy

The codebase supports two deployment modes:

1. **Modular Python files** - For Cloud Functions or local use
   - Clean separation, testable modules
   - `main.py:28-42` - Cloud Function decorator

2. **Inline Python in YAML** - For GitHub Actions
   - Self-contained, no deployment step
   - `.github/workflows/daily-report.yml:34-359`

The GitHub Actions workflow contains a complete copy of all logic inline, allowing the workflow to run without installing the module files.

## Change Indicator Calculation

Daily change is computed by comparing last two history entries:

**Reference:** `html_generator.py:73-98`

- Green down arrow (decrease) = positive progress
- Red up arrow (increase) = files added
- Gray arrow = no change

This inverts typical "up is good" UX because the goal is file reduction.
