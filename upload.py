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

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Header row
#    0        1         2              3             4              5
# Person	Date	Workout Name	Duration	Exercise Name	Set Order
# NOTE: Ensure your Google Sheets Date column is formatted to INCLUDE
# NOTE: leading 0's on all componenets. Strong's CSV export includes them.
# NOTE: Without this formatting, duplicate rows will not be detected, as
# NOTE: this current implementation does a string comparison, not a
# NOTE: logical date comparison.
PERSON = 0
DATE = 1
WORKOUT_NAME = 2
DURATION = 3
EXERCISE_NAME = 4
SET_ORDER = 5

# For deduplication of data, we must figure out which rows of the incoming
# data match a row in the existing data. To do this accurately, we need
# to be able to uniquely identify a row.
UNIQUE_ROW_KEY = [
    PERSON,
    DATE,
    WORKOUT_NAME,
    DURATION,
    EXERCISE_NAME,
    SET_ORDER,
]


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


def read_existing_data(
    creds,
    spreadsheet_id: str,
    sheet_name: str,
) -> list[list]:
    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found")
            return

        print(f"Read {len(values)} rows from {spreadsheet_id} -> {sheet_name}")

        return values
    except HttpError as err:
        print(err)


def read_data_to_upload(
    person: str,
    filename: str,
) -> list[list]:
    with open(filename, "r") as file:
        reader = csv.reader(file)
        raw = list(reader)[1:]  # Exclude header row

    return [[person] + row for row in raw]


def _rows_to_dict(data: list[list]) -> dict[str, list]:
    result = {}
    for row in data:
        key_components = [f"{row[column_number]}" for column_number in UNIQUE_ROW_KEY]
        key = "|".join(key_components)
        result[key] = row
    return result


def deduplicate(
    existing_data: list[list],
    data_to_upload: list[list],
) -> list[list]:
    existing_data_lookup = _rows_to_dict(existing_data)
    data_to_upload_lookup = _rows_to_dict(data_to_upload)
    deduped = []
    duplicate_count = 0
    for k, v in data_to_upload_lookup.items():
        if k in existing_data_lookup:
            # Duplicate row, skip
            duplicate_count += 1
            continue
        print(f"{k} not found in existing data")
        deduped.append(v)
    print(f"Removed {duplicate_count} duplicate row(s) from input data")
    return deduped


def upload(
    creds,
    spreadsheet_id: str,
    sheet_name: str,
    data: list[list],
):

    # The exports from the Strong app obviously don't include a first name column
    # but distinguishing between personal exports is necessary when analyzing
    # a group of people's lifting data together, such as the use-case that
    # inspired this script.
    print(f"Attempting to upload {len(data)} rows to sheet")

    try:
        service = build("sheets", "v4", credentials=creds)

        value_range_body = {"values": data}
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
    existing_data = read_existing_data(creds, args.spreadsheet_id, args.sheet_name)
    data_to_upload = read_data_to_upload(args.person, args.filename)
    deduped = deduplicate(existing_data, data_to_upload)
    if not deduped:
        print("Entire input file has already been uploaded")
        exit(0)
    upload(creds, args.spreadsheet_id, args.sheet_name, deduped)
