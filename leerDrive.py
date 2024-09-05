import pandas as pd
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread
import csv
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib
from google_auth_oauthlib.flow import InstalledAppFlow
import base64
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from datetime import date, datetime, timedelta

Error = 0

# Parse file paths from command-line arguments
def get_file_paths():
    parser = argparse.ArgumentParser(description="Input the file paths for token.json and key.json")
    parser.add_argument("--token", required=True, help="Path to the token.json file")
    parser.add_argument("--key", required=True, help="Path to the key.json file")
    args = parser.parse_args()
    return args.token, args.key

def app(token_file, key_file):
    with open('/mnt/Intmed/log.log', 'a') as archivo:
        current = str(datetime.now())    
        archivo.write(f'Inicia descarga: {current}\n')
        archivo.close()

    SCOPES = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    
    SPREADSHEET_ID = '1Eir8RUAYURiPAA_YlJ0-H-FuKPPVvNBpC1nM9GoS18A'
    
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:BQ25000').execute()

    data1 = result.get('values', [])
    df = pd.DataFrame(data1)

    print("Inicia importación a csv...")

    filepath = Path(r'/mnt/Intmed/Drive.csv')
    df.to_csv(filepath, index=False, encoding='cp1252') 
    
    with open('/mnt/Intmed/Drive.csv',"r", errors='ignore') as f:
        row_count = sum(1 for row in f)
        print(row_count)
        f.close()

    with open('/mnt/Intmed/log.log','a') as archivo:
        archivo.write(f'Termina descarga: {current}\n')
        archivo.write(f'Filas descargadas: {row_count}\n')
        archivo.close()

    send_email(token_file)

def send_email(token_file):  
    SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES_GMAIL)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES_GMAIL)
            creds = flow.run_local_server(port=0)
    
    service = build('gmail', 'v1', credentials=creds)

    # Create the email
    message = MIMEMultipart()
    if Error == 0:
        message['to'] = 'efigueroa@ingenes.com'
        message['subject'] = 'Gran consolidado IntMed'
        msg = MIMEText('Descarga realizada con exito.')
    
    if Error == 1:
        message['to'] = 'efigueroa@ingenes.com'
        message['subject'] = 'Gran consolidado IntMed'
        msg = MIMEText('Error en descarga.')

    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the email
    send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
    print(f"Message Id: {send_message['id']}")

# Main execution block
if __name__ == "__main__":
    try:
        token_file, key_file = get_file_paths()
        app(token_file, key_file)
    except Exception as error:
        with open('/mnt/Intmed/log.log','a') as archivo:
            current = str(datetime.now())    
            archivo.write(f'Error en descarga: {current}\n')
            archivo.write(f'Error: {repr(error)}\n')
            archivo.close()
        Error = 1
        send_email(token_file)
