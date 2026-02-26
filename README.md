# 📊 Domoticz → Google Sheets Backup

> Automatically sync your Domoticz sensor data to Google Sheets — with offline buffering, error logging, and cron automation.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔄 Auto-sync | Periodically fetches all Domoticz devices via API |
| ☁️ Google Sheets | Uploads data directly to your spreadsheet |
| 💾 Local buffer | Saves data locally if internet/Domoticz is unavailable |
| 📤 Auto-retry | Sends buffered data automatically on next run |
| 📝 Logging | All actions and errors logged to file |

---

## 🧰 Requirements

- Python 3.x
- Domoticz running on Raspberry Pi (or any server)
- Google Cloud project with a Service Account

**Install Python dependencies:**

```bash
pip3 install requests gspread google-auth
```

---

## ⚙️ Setup

### 1. Google Sheets

1. Create a new Google Sheet, name it e.g. `DomoticzBackup`
2. Name the first worksheet `Data`
3. Add headers manually in row 1:

```
Timestamp | Name | idx | Value | Unit
```

---

### 2. Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the following APIs:
   - **Google Sheets API**
   - **Google Drive API**

---

### 3. Service Account & Credentials

1. Go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**, e.g. `domoticz-backup-sa`
3. Go to **Keys → Add Key → Create new key → JSON**
4. Download the JSON file and save it on your Raspberry Pi:

```bash
/home/pi/credentials.json
```

5. Restrict file permissions:

```bash
chmod 600 /home/pi/credentials.json
```

6. Copy the `client_email` from the JSON file and **share your Google Sheet** with that address (grant **Editor** access)

---

### 4. Script Configuration

Save the script as `/home/pi/domoticz_backup.py` and update these variables:

```python
DOMOTICZ_URL = "http://127.0.0.1/json.htm?type=command&param=getdevices&filter=all&used=true&order=Name"
SPREADSHEET_NAME = "DomoticzBackup"
WORKSHEET_NAME   = "Data"
CREDENTIALS_FILE = "/home/pi/credentials.json"
BUFFER_FILE      = "/home/pi/domoticz_buffer.csv"
LOG_FILE         = "/home/pi/domoticz_backup.log"
```

> **Note:** Domoticz 2023.2+ changed the API format.  
> Use `type=command&param=getdevices` instead of the old `type=devices`.

---

### 5. Test the Script

```bash
python3 /home/pi/domoticz_backup.py
```

- Check logs: `cat /home/pi/domoticz_backup.log`
- Check your Google Sheet for uploaded rows ✅

---

## ⏰ Automate with Cron

Run the script every 15 minutes:

```bash
crontab -e
```

Add this line:

```cron
*/15 * * * * /usr/bin/python3 /home/pi/domoticz_backup.py >> /home/pi/domoticz_backup.log 2>&1
```

---
