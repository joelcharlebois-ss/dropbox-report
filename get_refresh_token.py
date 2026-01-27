"""Script to obtain Dropbox refresh token via OAuth2 flow."""

import os
import requests
import base64
import webbrowser
from dotenv import load_dotenv

load_dotenv()

# Read from environment or prompt
APP_KEY = os.environ.get("DROPBOX_APP_KEY") or input("Enter Dropbox App Key: ").strip()
APP_SECRET = os.environ.get("DROPBOX_APP_SECRET") or input("Enter Dropbox App Secret: ").strip()

# Step 1: Generate authorization URL
auth_url = (
    f"https://www.dropbox.com/oauth2/authorize"
    f"?client_id={APP_KEY}"
    f"&response_type=code"
    f"&token_access_type=offline"
)

print("=" * 60)
print("DROPBOX OAUTH SETUP")
print("=" * 60)
print("\n1. Opening browser to authorize the app...\n")
print(f"   If browser doesn't open, visit:\n   {auth_url}\n")

webbrowser.open(auth_url)

print("2. After authorizing, Dropbox will show you a code.")
auth_code = input("\n   Paste the authorization code here: ").strip()

# Step 2: Exchange code for tokens
print("\n3. Exchanging code for tokens...")

token_url = "https://api.dropboxapi.com/oauth2/token"
auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

response = requests.post(
    token_url,
    headers={"Authorization": f"Basic {auth_header}"},
    data={
        "code": auth_code,
        "grant_type": "authorization_code"
    }
)

if response.status_code == 200:
    tokens = response.json()
    print("\n" + "=" * 60)
    print("SUCCESS! Update your .env file with these values:")
    print("=" * 60)
    print(f"\nDROPBOX_ACCESS_TOKEN={tokens['access_token']}")
    print(f"DROPBOX_REFRESH_TOKEN={tokens['refresh_token']}")
    print(f"DROPBOX_APP_KEY=<your-app-key>")
    print(f"DROPBOX_APP_SECRET=<your-app-secret>")
    print("\n" + "=" * 60)
else:
    print(f"\nError: {response.status_code}")
    print(response.text)
