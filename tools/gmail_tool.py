"""
Gmail Tool - Creates draft emails with benefit forms attached
"""
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any
from google.adk.tools import FunctionTool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


def authenticate_gmail():
    """Authenticate and return Gmail service"""
    creds = None
    
    # Check for existing token
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, request authorization
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Please download credentials.json from Google Cloud Console")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)


def gmail_draft_tool(
    to_email: str,
    subject: str,
    body: str,
    zip_file_path: str = None,
    from_email: str = None
) -> Dict[str, Any]:
    """
    Creates a Gmail draft email with optional attachment.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body text
        zip_file_path: Path to zip file to attach (optional)
        from_email: Sender email (uses env var if not provided)
    
    Returns:
        Dictionary with draft_id and status
    """
    try:
        service = authenticate_gmail()
        if not service:
            return {"status": "error", "message": "Gmail authentication failed"}
        
        # Create message
        message = MIMEMultipart()
        message['to'] = to_email
        message['subject'] = subject
        
        if from_email:
            message['from'] = from_email
        elif os.getenv('FROM_EMAIL'):
            message['from'] = os.getenv('FROM_EMAIL')
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachment if provided
        if zip_file_path and os.path.exists(zip_file_path):
            with open(zip_file_path, 'rb') as f:
                part = MIMEBase('application', 'zip')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(zip_file_path)}'
                )
                message.attach(part)
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')
        
        # Create draft
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        return {
            "status": "success",
            "draft_id": draft['id'],
            "message": f"Draft created successfully. Draft ID: {draft['id']}"
        }
    
    except HttpError as error:
        return {
            "status": "error",
            "message": f"Gmail API error: {error}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating draft: {str(e)}"
        }


# Create ADK Tool wrapper
# FunctionTool automatically extracts name and description from the function docstring and signature
gmail_draft_adk_tool = FunctionTool(gmail_draft_tool)

