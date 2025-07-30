import pandas as pd
import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate():
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials/credentials_email.json'

    # Remove invalid token file
    if os.path.exists(token_path) and os.path.getsize(token_path) == 0:
        os.remove(token_path)

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, sender, to, subject, body):
    try:
        message = create_message(sender, to, subject, body)
        send_message = service.users().messages().send(userId='me', body=message).execute()
        print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")

def main():
    sender_email = "YOUR_EMAIL_ADDRESS"  # Replace with your Gmail
    csv_file = r'match_score\cv_match_scores.csv'

    # Load data
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Filter applicants
    shortlisted = df[df['match_score'] > 80]

    if shortlisted.empty:
        print("⚠️ No applicants with match_score > 80")
        return

    # Authenticate Gmail API
    creds = authenticate()
    service = build('gmail', 'v1', credentials=creds)

    for _, row in shortlisted.iterrows():
        applicant_name = row['applicant_name']
        email = row['email']
        job = row['job_role']

        subject = f"Shortlisted for {job} Role"
        body = f"""
Dear {applicant_name},

We are pleased to inform you that you have been shortlisted for the position of {job} at our organization.

Your qualifications and experience align well with the requirements of the role, and we were impressed by your overall profile.

Our team will be reaching out to you shortly with the next steps in the selection process.

Thank you for your interest, and we look forward to the possibility of working together.

Best regards,  
HR Team
"""


        send_email(service, sender_email, email, subject, body)

if __name__ == '__main__':
    main()
