# Second-Chance Agent - Google ADK Multi-Agent System

A multi-agent system built with Google's Agent Development Kit (ADK) that helps laid-off workers discover and apply for unemployment benefits, SNAP, ACA subsidies, and free re-training vouchers.

## Problem

Every day thousands of Americans announce lay-offs on LinkedIn. Most never apply for the unemployment, SNAP, ACA subsidies or free re-training vouchers they qualify for—simply because the forms feel overwhelming and the rules are opaque. The average worker leaves $7,400 on the table.

## Solution

"Second-Chance Agent" converts a public lay-off post into a complete, ready-to-sign benefit packet in under 15 minutes using a multi-agent system.

## Architecture

### Agent 1 - Scout

- Runs every 30 minutes (can be deployed in Kaggle notebook)
- Monitors Google News RSS for LinkedIn layoff posts
- Extracts state abbreviation using regex
- Appends candidate data to `shared_state.jsonl`
- Triggers Agent 2 (Caseworker)

### Agent 2 - Caseworker

- Uses Gemini 1.5 Flash as a state-benefits expert
- Determines eligibility using `eligibility_engine_tool`
- Downloads blank PDF forms from Google Drive
- Fills forms using ADK's FormFillerTool
- Creates zip file of completed forms
- Drafts empathetic email with Gmail API

### Agent 3 - Watchdog

- Runs daily at 08:00 UTC
- Reads `shared_state.jsonl` and calculates statistics
- Posts anonymized stats to Twitter/X via API v2

## Quick Start

See [SETUP.md](SETUP.md) for detailed setup instructions.

### Basic Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables (see `.env.example`)

3. Authenticate APIs (first run only):

```bash
python -c "from tools.gmail_tool import authenticate_gmail; authenticate_gmail()"
python -c "from tools.drive_tool import authenticate_drive; authenticate_drive()"
```

4. Run agents:

```bash
# Agent 1 (Scout) - runs every 30 min
python main.py scout

# Agent 2 (Caseworker) - process pending cases
python main.py caseworker --all-pending

# Agent 3 (Watchdog) - runs daily at 08:00 UTC
python main.py watchdog
```

## Privacy & Ethics

- Only processes public LinkedIn posts
- No PII stored beyond profile URL and inferred state
- Recipients can ignore draft emails; no spam sent automatically
- MIT-licensed with opt-out instructions in every email footer

## Future Work

- Expand to all 50 states (currently 5)
- Add Spanish-language templates
- Integrate with state APIs for submitted claims (where OAuth available)

## License

MIT License - See LICENSE file for details
