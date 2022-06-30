from __future__ import print_function

import base64
import os.path
from bs4 import BeautifulSoup

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """
    Makes Gmail API request, extracts the last email object,
    decodes its body and returns it, together with its id and date
    """

    creds = None
    # the file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # if there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # call the Gmail API
    service = build('gmail', 'v1', credentials=creds)

    # query the causal-jobs folder of Gmail and get the latest email in it
    results = service.users().messages().list(maxResults=1, userId='me', q='in:causal-jobs').execute()
    messages = results.get('messages')

    for msg in messages:
        # get the message from its id
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        # get value of 'payload' from dictionary 'txt'
        payload = txt['payload']
        headers = payload['headers']

        # get date of the email
        semicolon_index = headers[1]['value'].find(';')
        date = headers[1]['value'][semicolon_index + 1:]

        # look for subject and sender email in the headers
        for d in headers:
            if d['name'] == 'Subject':
                subject = d['value']
            if d['name'] == 'From':
                sender = d['value']

        # the body of the message is in encrypted format
        # get the data and decode it with base 64 decoder
        parts = payload.get('parts')[0]
        data = parts['body']['data']
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # the data obtained is in lxml
        # parse it with BeautifulSoup library
        soup = BeautifulSoup(decoded_data, "lxml")
        body = soup.body()

        # return email body, email id, email date
        return body, msg['id'], date

if __name__ == '__main__':
    main()