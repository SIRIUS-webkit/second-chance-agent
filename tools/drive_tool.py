"""
Google Drive Tool - Downloads PDF forms from Google Drive
"""
import os
import io
from typing import List, Dict, Any
from google.adk.tools import Tool
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def authenticate_drive():
    """Authenticate and return Drive service"""
    creds = None
    
    if os.path.exists('token_drive.json'):
        creds = Credentials.from_authorized_user_file('token_drive.json', SCOPES)
    
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
        
        with open('token_drive.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)


def download_pdfs_from_drive(
    folder_id: str,
    state: str,
    output_dir: str = "forms"
) -> List[str]:
    """
    Downloads PDF forms from a Google Drive folder for a specific state.
    
    Args:
        folder_id: Google Drive folder ID containing PDF forms
        state: Two-letter state abbreviation
        output_dir: Directory to save downloaded PDFs
    
    Returns:
        List of downloaded PDF file paths
    """
    try:
        service = authenticate_drive()
        if not service:
            return []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Search for PDFs in the folder
        query = f"'{folder_id}' in parents and mimeType='application/pdf' and name contains '{state}'"
        results = service.files().list(
            q=query,
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        downloaded_paths = []
        
        for file in files:
            file_id = file['id']
            file_name = file['name']
            
            # Download file
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join(output_dir, file_name)
            
            with open(file_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            downloaded_paths.append(file_path)
            print(f"Downloaded: {file_name}")
        
        return downloaded_paths
    
    except HttpError as error:
        print(f"Drive API error: {error}")
        return []
    except Exception as e:
        print(f"Error downloading PDFs: {str(e)}")
        return []


def drive_download_tool(
    folder_id: str,
    state: str,
    output_dir: str = "forms"
) -> Dict[str, Any]:
    """
    ADK Tool wrapper for downloading PDFs from Google Drive.
    
    Args:
        folder_id: Google Drive folder ID
        state: State abbreviation
        output_dir: Output directory
    
    Returns:
        Dictionary with status and list of downloaded files
    """
    if not folder_id:
        folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '')
    
    if not folder_id:
        return {
            "status": "error",
            "message": "Google Drive folder ID not provided"
        }
    
    downloaded_files = download_pdfs_from_drive(folder_id, state, output_dir)
    
    return {
        "status": "success" if downloaded_files else "error",
        "files": downloaded_files,
        "count": len(downloaded_files),
        "message": f"Downloaded {len(downloaded_files)} PDF(s) for {state}"
    }


# Create ADK Tool wrapper
drive_download_adk_tool = Tool(
    name="drive_download",
    description="Downloads PDF forms from a Google Drive folder for a specific state. Use this to get blank benefit application forms.",
    func=drive_download_tool
)

