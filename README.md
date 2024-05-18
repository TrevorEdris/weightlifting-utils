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

## `analyze.py`

Analyze a given CSV file, producing a PDF file with multiple graphs of weightlifting trends over time.

```
❯ python analyze.py -h
usage: analyze.py [-h] [--input-file INPUT_FILE] [--output-dir OUTPUT_DIR]

Weightlifting Data Analyzer

options:
  -h, --help            show this help message and exit
  --input-file INPUT_FILE
                        Input CSV file path
  --output-dir OUTPUT_DIR
                        Directory to save output files
```

**NOTE:** Required CSV format

```csv
Person,Date,Workout Name,Duration,Exercise Name,Set Order,Weight,Reps,Distance,Seconds,Notes,Workout Notes,RPE
```

This format exactly matches the exports of the Strong iOS app with the addition of the `Person` column.
**Without this column, `analyze.py` will not work properly.**

### Example

```
❯ python analyze.py --input-file sample_input/sample_weightlifting_data.csv --output-dir output
2024-05-18 12:18:09,078 - Analyzing sample_input/sample_weightlifting_data.csv
2024-05-18 12:18:09,285 - Created output/graphs/avg_weight_per_exercise_Alice.png
2024-05-18 12:18:09,405 - Created output/graphs/avg_weight_per_exercise_Bob.png
2024-05-18 12:18:09,509 - Created output/graphs/avg_weight_per_exercise_Chris.png
2024-05-18 12:18:09,613 - Created output/graphs/avg_weight_per_exercise_Emily.png
2024-05-18 12:18:09,713 - Created output/graphs/avg_weight_per_exercise_Trevor.png
2024-05-18 12:18:09,818 - Created output/graphs/avg_weight_per_person_Bench Press (Barbell).png
2024-05-18 12:18:09,929 - Created output/graphs/avg_weight_per_person_Deadlift (Barbell).png
2024-05-18 12:18:10,034 - Created output/graphs/avg_weight_per_person_Squat (Barbell).png
2024-05-18 12:18:10,160 - Created output/graphs/total_weight_lifted_per_person.png
2024-05-18 12:18:10,473 - Saved PDF to output/out.pdf
```

See the [sample PDF](./sample_output/out.pdf) for an example of what the output looks like.


## `generate_sample_data.py`

Generate a sample CSV file with 90 days of random lifting data, showing progressive increase in strength for 5 people.

```
❯ python generate_sample_data.py
```

**NOTE:** This will overwrite `sample_input/sample_weightlifting_data.csv`.
