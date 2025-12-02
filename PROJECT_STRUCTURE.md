# Project Structure

```
ai-agent-adk-hackthon/
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── scout.py              # Agent 1: RSS monitoring & state extraction
│   ├── caseworker.py         # Agent 2: Eligibility & form processing
│   └── watchdog.py           # Agent 3: Daily stats & Twitter posting
│
├── tools/                     # Custom ADK tools
│   ├── __init__.py
│   ├── eligibility_engine.py # Determines benefit eligibility
│   ├── gmail_tool.py         # Gmail draft creation
│   ├── form_filler.py        # PDF form filling
│   └── drive_tool.py         # Google Drive PDF downloads
│
├── utils/                     # Utility functions
│   ├── __init__.py
│   └── shared_state.py       # Shared state management (JSONL)
│
├── forms/                     # Downloaded PDF forms (created at runtime)
│   └── {state}/              # State-specific forms
│
├── output/                    # Generated zip files (created at runtime)
│
├── main.py                   # Main entry point
├── test_agents.py            # Test script for components
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
├── SETUP.md                  # Detailed setup guide
├── LICENSE                   # MIT License
├── .env.example              # Environment variables template
└── .gitignore                # Git ignore rules
```

## Key Files

### Agents

- **scout.py**: Monitors Google News RSS for LinkedIn layoff posts every 30 minutes. Extracts state information and triggers Caseworker agent.

- **caseworker.py**: Processes layoff posts:
  1. Determines eligibility using eligibility_engine_tool
  2. Downloads state-specific PDF forms from Google Drive
  3. Fills forms with extracted information
  4. Creates zip file of completed forms
  5. Drafts empathetic email with Gmail API

- **watchdog.py**: Runs daily at 08:00 UTC:
  1. Reads shared_state.jsonl
  2. Calculates statistics (total amount unlocked, cases processed)
  3. Posts anonymized stats to Twitter/X

### Tools

- **eligibility_engine.py**: Determines which benefit programs (UI, SNAP, ACA, RETRAINING) a worker qualifies for based on state and post content. Returns programs list and estimated total amount.

- **gmail_tool.py**: Creates Gmail draft emails with optional attachments. Handles OAuth authentication.

- **form_filler.py**: Fills PDF forms (AcroForms) with applicant information. Uses PyPDF2/pypdf for PDF manipulation.

- **drive_tool.py**: Downloads PDF forms from Google Drive folder. Searches for state-specific forms.

### Utilities

- **shared_state.py**: Manages `shared_state.jsonl` file:
  - Appends new entries
  - Reads all entries
  - Calculates statistics
  - Tracks processing status

## Data Flow

1. **Scout** → Monitors RSS → Extracts state → Writes to `shared_state.jsonl` → Triggers **Caseworker**

2. **Caseworker** → Reads from `shared_state.jsonl` → Determines eligibility → Downloads PDFs → Fills forms → Creates zip → Drafts email → Updates `shared_state.jsonl`

3. **Watchdog** → Reads `shared_state.jsonl` → Calculates stats → Posts to Twitter

## Runtime Files

- `shared_state.jsonl`: JSON Lines file tracking all processed posts
- `credentials.json`: Google OAuth credentials (not in repo)
- `token.json`: Gmail OAuth token (not in repo)
- `token_drive.json`: Drive OAuth token (not in repo)
- `forms/`: Directory with downloaded PDF forms
- `output/`: Directory with generated zip files

