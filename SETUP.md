# Setup Guide for Second-Chance Agent

## Prerequisites

1. Python 3.9 or higher
2. Google Cloud account (for Gemini API, Gmail API, Drive API)
3. Twitter Developer account (for API v2)
4. Google Drive folder with PDF forms (one per state)

## Step-by-Step Setup

### 1. Clone and Install Dependencies

```bash
cd ai-agent-adk-hackthon
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### A. Enable APIs

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Generative AI API (for Gemini)
   - Gmail API
   - Google Drive API

#### B. Create API Credentials

1. Go to "APIs & Services" > "Credentials"
2. Create OAuth 2.0 Client ID (for Gmail and Drive)
3. Download credentials as `credentials.json` and place in project root
4. Create API Key for Gemini API

#### C. Authenticate Gmail and Drive

Run the authentication flow (first time only):

```bash
python -c "from tools.gmail_tool import authenticate_gmail; authenticate_gmail()"
python -c "from tools.drive_tool import authenticate_drive; authenticate_drive()"
```

This will open a browser window for OAuth consent. After authentication, `token.json` and `token_drive.json` will be created.

### 3. Twitter API Setup

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Generate API keys and tokens:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
   - Bearer Token

### 4. Google Drive Folder Setup

1. Create a Google Drive folder
2. Upload PDF forms for each state (e.g., `CA_UI.pdf`, `CA_SNAP.pdf`, etc.)
3. Make the folder publicly accessible (or share with service account)
4. Copy the folder ID from the URL

### 5. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```
GOOGLE_API_KEY=your_gemini_api_key
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
FROM_EMAIL=your_email@gmail.com
```

### 6. Create Required Directories

```bash
mkdir -p forms output
```

## Running the Agents

### Agent 1 - Scout (RSS Monitor)

Runs every 30 minutes, monitors LinkedIn layoff posts:

```bash
python main.py scout
# or
python agents/scout.py
```

### Agent 2 - Caseworker (Form Processor)

Processes pending cases:

```bash
# Process all pending entries
python main.py caseworker --all-pending

# Process specific LinkedIn URL
python main.py caseworker --url "https://www.linkedin.com/posts/..."

# or
python agents/caseworker.py --all-pending
```

### Agent 3 - Watchdog (Daily Stats)

Runs daily at 08:00 UTC, posts stats to Twitter:

```bash
python main.py watchdog
# or
python agents/watchdog.py
```

## Testing Individual Components

### Test Eligibility Engine

```python
from tools.eligibility_engine import eligibility_engine_tool
result = eligibility_engine_tool("CA", "I was laid off from my job")
print(result)
```

### Test Form Filler

```python
from tools.form_filler import form_filler_adk_tool
result = form_filler_adk_tool.func(
    pdf_path="forms/CA/CA_UI.pdf",
    output_path="output/test_filled.pdf",
    name="John Doe",
    address="123 Main St, Los Angeles, CA 90001",
    employer="Tech Corp",
    wage="75000"
)
print(result)
```

## Deployment Options

### Option 1: Kaggle Notebook (Free)

- Upload Scout agent to Kaggle
- Use Kaggle's free GPU/CPU resources
- Set up scheduled runs

### Option 2: Google Cloud Run

- Containerize the agents
- Deploy to Cloud Run
- Set up Cloud Scheduler for cron jobs

### Option 3: Local Server/VPS

- Run agents as systemd services
- Use cron for scheduling

## Troubleshooting

### Gmail API Issues

- Ensure OAuth consent screen is configured
- Check that scopes are correct
- Verify `credentials.json` is in project root

### Drive API Issues

- Ensure folder is shared correctly
- Check folder ID is correct
- Verify API is enabled

### Twitter API Issues

- Check API v2 access level
- Verify bearer token is correct
- Ensure app has write permissions

### PDF Form Issues

- Ensure PDFs have form fields (AcroForms)
- Check PDF paths are correct
- Verify PyPDF2/pypdf can read the PDFs

## Notes

- The system uses `shared_state.jsonl` to track processed posts
- Forms are cached in `forms/` directory
- Output zip files are stored in `output/` directory
- Email addresses need to be extracted or provided separately (LinkedIn doesn't expose emails)

## Privacy & Ethics

- Only processes public LinkedIn posts
- No PII stored beyond profile URL and state
- Recipients can ignore draft emails
- Includes opt-out instructions in every email
