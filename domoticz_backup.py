

import requests
import gspread
import csv
import os
from datetime import datetime
from google.oauth2.service_account import Credentials

# =======================
# CONFIG
# ======================

DOMOTICZ_URL = "http://127.0.0.1/json.htm?type=command&param=getdevices&filter=all&used=true&order=Name"
SPREADSHEET_NAME = "DomoticzBackup"
WORKSHEET_NAME = "Data"
CREDENTIALS_FILE = "/home/pi/credentials.json"
BUFFER_FILE = "/home/pi/domoticz_buffer.csv"
LOG_FILE = "/home/pi/domoticz_backup.log"
MAX_ROWS = 2000
TRIM_ROWS = 500

# =======================

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

def get_domoticz_data():
    try:
        response = requests.get(DOMOTICZ_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"Domoticz error: {e}")
        return None

def parse_devices(data):
    rows = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for device in data.get("result", []):
        name = device.get("Name", "")
        idx = device.get("idx", "")
        value = device.get("Data", "")

        rows.append([timestamp, name, idx, value])

    return rows

def append_to_buffer(rows):
    with open(BUFFER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    log(f"Buffered {len(rows)} rows")

def send_to_sheets(rows):
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    current_rows = len(sheet.get_all_values())
    if current_rows >= MAX_ROWS:
        sheet.delete_rows(2, TRIM_ROWS)
        log(f"Trimmed {TRIM_ROWS} oldest rows (was {current_rows})")

    sheet.append_rows(rows, value_input_option="RAW")

def send_buffer_if_exists():
    if not os.path.exists(BUFFER_FILE):
        return

    try:
        with open(BUFFER_FILE, "r") as f:
            reader = list(csv.reader(f))

        if reader:
            send_to_sheets(reader)
            os.remove(BUFFER_FILE)
            log(f"Sent buffered data ({len(reader)} rows)")
    except Exception as e:
        log(f"Buffer send failed: {e}")

def main():
    data = get_domoticz_data()
    if not data:
        return

    rows = parse_devices(data)

    try:
        send_buffer_if_exists()
        send_to_sheets(rows)
        log(f"Sent {len(rows)} rows")
    except Exception as e:
        log(f"Sheets error: {e}")
        append_to_buffer(rows)

if __name__ == "__main__":
    main()
