"""
Shared State Management - Handles shared_state.jsonl file operations
"""
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


SHARED_STATE_FILE = "shared_state.jsonl"


def append_to_shared_state(data: Dict[str, Any]) -> bool:
    """
    Appends a new entry to shared_state.jsonl
    
    Args:
        data: Dictionary with candidate data
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure data has required fields
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()
        
        # Append to JSONL file
        with open(SHARED_STATE_FILE, 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        return True
    except Exception as e:
        print(f"Error appending to shared state: {e}")
        return False


def read_shared_state() -> List[Dict[str, Any]]:
    """
    Reads all entries from shared_state.jsonl
    
    Returns:
        List of dictionaries with all entries
    """
    entries = []
    
    if not os.path.exists(SHARED_STATE_FILE):
        return entries
    
    try:
        with open(SHARED_STATE_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Error reading shared state: {e}")
    
    return entries


def get_statistics() -> Dict[str, Any]:
    """
    Calculates statistics from shared_state.jsonl
    
    Returns:
        Dictionary with total_amount_unlocked, total_rows, etc.
    """
    entries = read_shared_state()
    
    total_amount = sum(
        entry.get("amount_unlocked", 0) 
        for entry in entries 
        if isinstance(entry.get("amount_unlocked"), (int, float))
    )
    
    return {
        "total_amount_unlocked": round(total_amount, 2),
        "total_rows": len(entries),
        "entries": entries
    }


def mark_as_processed(linkedin_url: str) -> bool:
    """
    Marks an entry as processed (optional - could add status field)
    
    Args:
        linkedin_url: LinkedIn URL to mark as processed
    
    Returns:
        True if successful
    """
    # This could be enhanced to update entries in place
    # For now, we'll rely on timestamp-based filtering
    return True

