#.\myenv\Scripts\activate En esta ruta: C:\Users\ebfigueroa\Documents\VSCode\Phyton>
from conection import get_connection
import pandas as pd
import numpy as np

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread

import csv
import pyodbc

#Correo:
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

def app():

    with open('log.log', 'a') as archivo:
        current = str(datetime.now())    
        archivo.write(f'Inicia descarga: {current}\n')
        archivo.close()

    SCOPES = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    KEY = 'key.json'
    SPREADSHEET_ID = '1Eir8RUAYURiPAA_YlJ0-H-FuKPPVvNBpC1nM9GoS18A'
    #'1bsT8HhlZ2JX5cIuvWOegIKuAOca4rNd-EEVr4lahxjI'

    creds = None
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=SCOPES)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='A1:BQ25000').execute()

    data1 = result.get('values', [])
    df=pd.DataFrame(data1)

    print("Inicia importación a csv...")

    #filepath = Path('C:/Users/ebfigueroa/Documents/VSCode/Phyton/InteligenciaMedica/Reportes/Drive.csv')
    filepath = Path(r'\\192.168.71.10\IntMed\GranConsolidado\Drive.csv')
    #filepath = Path(r'\\192.168.1.6\IntMed\GranConsolidado\Drive.csv')
    df.to_csv(filepath, index=False, encoding='cp1252') 
    
    
    #print(df)
    #ContadorF = df.count(axis=1)
    #print(ContadorF)
    
    with open('C:/Users/ebfigueroa/Documents/VSCode/Phyton/InteligenciaMedica/Reportes/Drive.csv',"r", errors='ignore') as f:
        row_count = sum(1 for row in f)
        print(row_count)
        f.close()

    #print(data1)
    with open('log.log','a') as archivo:
        archivo.write(f'Termina descarga: {current}\n')
        archivo.write(f'Filas descargadas: {row_count}\n')
        archivo.close()
   
    send_email()

def send_email():  
    SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.send']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES_GMAIL)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES_GMAIL)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    
    service = build('gmail', 'v1', credentials=creds)

    # Create the email
    message = MIMEMultipart()
    if Error==0:
        message['to'] = 'efigueroa@ingenes.com'
        message['subject'] = 'Gran consolidado IntMed'
        msg = MIMEText('Descarga realizada con exito.')
    
    if  Error==1:
        message['to'] = 'efigueroa@ingenes.com'
        message['subject'] = 'Gran consolidado IntMed'
        msg = MIMEText('Error en descarga.')

    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the email
    send_message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()

    print(f"Message Id: {send_message['id']}")


#
try:
    app()
except Exception as error:
    with open('log.log','a') as archivo:
        current = str(datetime.now())    
        archivo.write(f'Error en descarga: {current}\n')
        archivo.write(f'Error: {repr(error)}\n')
        archivo.close()
    Error = 1

    send_email()
