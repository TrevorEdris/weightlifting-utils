import argparse
import csv
import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

CREDS_DIR = "creds"
TOKEN_FILE = f"{CREDS_DIR}/token.json"
CREDENTIALS_FILE = f"{CREDS_DIR}/creds.json"

SPREADSHEET_ID = "1JJxZRA4OnsbzUOaL6aYvD5qSf1uq2uoO9Ew1c-TFIH4"
SHEET_NAME = "Combined Data"


def auth(credentials_file: str):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if not os.path.exists(CREDS_DIR):
        os.mkdir(CREDS_DIR)

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


def upload(
    creds,
    person: str,
    filename: str,
    spreadsheet_id: str,
    sheet_name: str,
):
    with open(filename, "r") as file:
        reader = csv.reader(file)
        raw = list(reader)[1:]  # Exclude header row

    # The exports from the Strong app obviously don't include a first name column
    # but distinguishing between personal exports is necessary when analyzing
    # a group of people's lifting data together, such as the use-case that
    # inspired this script.
    rows = [[person] + row for row in raw]
    print(f"Attempting to upload {len(rows)} rows to sheet")

    try:
        service = build("sheets", "v4", credentials=creds)

        value_range_body = {"values": rows}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            body=value_range_body,
        ).execute()

        print("Success")
    except HttpError as err:
        print("Failure")
        print(err)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Append CSV data to Google Sheets")
    parser.add_argument(
        "-c",
        "--credentials",
        default=CREDENTIALS_FILE,
        help="Path to Google Sheets credentials JSON file",
    )
    parser.add_argument(
        "-p", "--person", required=True, help="First name of person the data belongs to"
    )
    parser.add_argument(
        "-f", "--filename", required=True, help="Path to CSV file with data to upload"
    )
    parser.add_argument(
        "-i",
        "--spreadsheet-id",
        default=SPREADSHEET_ID,
        help="Google Sheets spreadsheet ID",
    )
    parser.add_argument("-s", "--sheet-name", default=SHEET_NAME, help="Sheet name")
    args = parser.parse_args()

    creds = auth(args.credentials)
    upload(creds, args.person, args.filename, args.spreadsheet_id, args.sheet_name)
