import base64
import os
import pickle
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config.settings import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_PATH = "tocken.pickle"
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")

class GmailService:
    """
    Handling GMAIL OAuth2 authentication and email sending
    """

    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        #Load exisitng token if avialable
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as f:
                creds = pickle.load(f)

        #Refresh or re-authenticate if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_PATH, "wb") as f:
                pickle.dump(creds,f)
        return build("gmail","v1", credentials=creds)
    
    def send_digest(self, html_content:str) -> bool:
        """Send the HTML email digest to the configured recepient."""
        try:
            subject = f"Stock News Digest - {date.today().strftime('%B %d, %Y')}"

            message = MIMEMultipart('alternative')
            message["Subject"]= subject
            message["From"] = settings.gmail_sender
            message["To"] = settings.gmail_recipient

            #Attach both plain text fallback and HTML
            plain_fallback = "Your email client does not support HTML. Please view this email in a modern client"
            message.attach(MIMEText(plain_fallback, "plain"))
            message.attach(MIMEText(html_content, "html"))

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            self.service.users().messages().send(
                userId="me", body={"raw":raw}
            ).execute()

            print(f"Email sent to {settings.gmail_recipient}")
            return True
        except Exception as e:
            print(f"Email failed to send.")
            return False