import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/blogger"]
CLIENT_SECRET_FILE = "client_secret.json"
OUTPUT_FILE = "generated_token.json"


def main():
    client_path = Path(CLIENT_SECRET_FILE)
    if not client_path.exists():
        raise FileNotFoundError(
            f"{CLIENT_SECRET_FILE} not found. Download your OAuth client JSON from Google Cloud and place it here."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
    )

    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
    )

    data = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token": creds.token,
        "token_uri": creds.token_uri,
        "scopes": list(creds.scopes or SCOPES),
    }

    Path(OUTPUT_FILE).write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n=== COPY THESE INTO GITHUB SECRETS ===")
    print(f"GOOGLE_CLIENT_ID={creds.client_id}")
    print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print(f"\nSaved full token details to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
