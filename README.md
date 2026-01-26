# Dropbox Folder File Counter

A Python tool that runs on Google Cloud Functions to scan a Dropbox folder recursively, count direct files in each subfolder, and generate an interactive HTML report uploaded to Google Drive.

## Features

- Recursively scans all subfolders in a Dropbox directory
- Counts direct files per folder (not recursive totals)
- Includes empty folders with 0 count
- Generates interactive HTML report with sortable, searchable table
- Uploads report to Google Drive for easy sharing
- Designed to run daily via Cloud Scheduler

## Project Structure

```
dropbox-folder-counter/
├── main.py                 # Cloud Function entry point
├── dropbox_scanner.py      # Dropbox API logic
├── html_generator.py       # HTML report generation
├── gdrive_uploader.py      # Google Drive upload logic
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
└── README.md               # This file
```

## Prerequisites

- Python 3.9+
- Google Cloud Platform account
- Dropbox account with API access
- Google Drive folder for report storage

## Setup Instructions

### 1. Dropbox API Setup

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access" and "Full Dropbox" (or "App folder" if you prefer)
4. Name your app and create it
5. Under "Permissions", enable:
   - `files.metadata.read`
6. Under "Settings", generate an access token
7. Copy the token for later use

### 2. Google Cloud Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Cloud Functions API
   - Cloud Scheduler API
   - Google Drive API

### 3. Google Service Account Setup

1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Name it (e.g., "dropbox-folder-counter")
4. Grant the role `Cloud Functions Invoker` (for scheduled invocation)
5. Click "Done"
6. Click on the created service account
7. Go to "Keys" tab > "Add Key" > "Create new key"
8. Select JSON and download the key file
9. Base64 encode the JSON file:
   ```bash
   # Linux/Mac
   base64 -w 0 service-account.json > credentials.b64

   # Windows PowerShell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("service-account.json"))
   ```

### 4. Google Drive Folder Setup

1. Create a folder in Google Drive where reports will be stored
2. Get the folder ID from the URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`
3. Share the folder with the service account email (found in the JSON key file)
   - Use "Editor" permission

### 5. Local Testing

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
4. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```
5. Run locally:
   ```bash
   python main.py
   ```

### 6. Deploy to Google Cloud Functions

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy the function
gcloud functions deploy dropbox-folder-counter \
  --gen2 \
  --runtime python39 \
  --region us-central1 \
  --trigger-http \
  --entry-point main \
  --memory 256MB \
  --timeout 540s \
  --set-env-vars "DROPBOX_ACCESS_TOKEN=your-token,DROPBOX_ROOT_PATH=/path/to/scan,GOOGLE_DRIVE_FOLDER_ID=your-folder-id,GOOGLE_CREDENTIALS_JSON=your-base64-credentials,MAKE_FILE_PUBLIC=false"
```

**Note:** For sensitive values, consider using Google Secret Manager instead of environment variables.

### 7. Set Up Cloud Scheduler

```bash
# Get the function URL
FUNCTION_URL=$(gcloud functions describe dropbox-folder-counter --region us-central1 --format='value(serviceConfig.uri)')

# Create a daily schedule (runs at 9 AM UTC)
gcloud scheduler jobs create http dropbox-counter-daily \
  --location us-central1 \
  --schedule "0 9 * * *" \
  --uri "$FUNCTION_URL" \
  --http-method POST \
  --oidc-service-account-email YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DROPBOX_ACCESS_TOKEN` | Yes | Dropbox API access token |
| `DROPBOX_ROOT_PATH` | No | Root folder to scan (default: root `/`) |
| `GOOGLE_DRIVE_FOLDER_ID` | Yes | Target Google Drive folder ID |
| `GOOGLE_CREDENTIALS_JSON` | Yes | Base64-encoded service account JSON |
| `MAKE_FILE_PUBLIC` | No | Set to `true` to make file publicly accessible |

## HTML Report Features

- **Sortable columns**: Click column headers to sort
- **Search**: Filter folders by path
- **Pagination**: Navigate large folder lists
- **Statistics**: Total folder and file counts
- **Responsive**: Works on desktop and mobile

## Troubleshooting

### "Missing required environment variable"
Ensure all required environment variables are set. Check with:
```bash
gcloud functions describe dropbox-folder-counter --region us-central1
```

### "Dropbox API Error"
- Verify your access token is valid
- Check the token has the required permissions
- Ensure the root path exists

### "Google Drive permission denied"
- Verify the service account email has access to the target folder
- Check the folder ID is correct
- Ensure Google Drive API is enabled

### Large folder timeouts
For very large Dropbox folders, increase the function timeout:
```bash
gcloud functions deploy dropbox-folder-counter --timeout 540s
```

## License

MIT License
