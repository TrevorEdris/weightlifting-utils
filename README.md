# weightlifting-utils
Utilities to make it easier to analyze weightlifting data, particularly from the Strong iOS app

## `upload.py`

This is a script that uses the Google Sheets python SDK to append
data from a local CSV file to an existing Google Sheets document.
The authorization logic is taken directly from the [Quickstart
guide from Google](https://developers.google.com/sheets/api/quickstart/python). Follow instructions there to create your
own set of credentials. Use the `-c` or `--credentials` flags
to point to your credentials JSON file. Alternatively, place
them in `creds/creds.json`.

```
❯ python upload.py -h
usage: upload.py [-h] [-c CREDENTIALS] -p PERSON -f FILENAME [-i SPREADSHEET_ID] [-s SHEET_NAME]

Append CSV data to Google Sheets

options:
  -h, --help            show this help message and exit
  -c CREDENTIALS, --credentials CREDENTIALS
                        Path to Google Sheets credentials JSON file
  -p PERSON, --person PERSON
                        First name of person the data belongs to
  -f FILENAME, --filename FILENAME
                        Path to CSV file with data to upload
  -i SPREADSHEET_ID, --spreadsheet-id SPREADSHEET_ID
                        Google Sheets spreadsheet ID
  -s SHEET_NAME, --sheet-name SHEET_NAME
                        Sheet name
```

### Example

```
❯ python upload.py -p Trevor -f strong.csv
Attempting to upload 25 rows to sheet
Success
```
