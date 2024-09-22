from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
from datetime import datetime

# Define the file to be uploaded and the folder in Google Drive (optional)
FILE_PATH = "./db.sqlite3"  # Change this to your file path
PARENT_FOLDER_ID = "1lxI0aCMO1ilM6S_xGMpoAheMQpdyOov_"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
service_account_file = 'service_account.json'


# Google Drive authentication
def authenticate_drive():
    creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=SCOPES)
    return creds

# Upload file to Google Drive
def upload_file():
    creds = authenticate_drive()
    service = build('drive', 'v3', credentials=creds)
    date = str(datetime.now().strftime("%m-%d-%Y"))
    upload_file_name = 'db.sqlite3-' + date
    file_metadata = {
        'name': upload_file_name,
        'parents': [PARENT_FOLDER_ID]
    }
    media = MediaFileUpload(FILE_PATH, mimetype='application/octet-stream')  # You can adjust the mimetype if necessary
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

# Schedule the task for daily upload at 12 AM
def schedule_task():
    upload_file()

if __name__ == '__main__':
    print("Running upload")
    schedule_task()
