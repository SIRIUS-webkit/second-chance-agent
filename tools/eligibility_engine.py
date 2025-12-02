"""
Eligibility Engine Tool - Determines benefit eligibility based on state and post content
"""
import os
from typing import Dict, List, Any
from google.adk.tools import FunctionTool


def eligibility_engine_tool(state: str, post_text: str) -> Dict[str, Any]:
    """
    Determines which benefit programs a laid-off worker qualifies for based on state and post content.
    
    Args:
        state: Two-letter state abbreviation (e.g., "CA", "NY", "TX")
        post_text: The LinkedIn post text content
    
    Returns:
        Dictionary with programs list and estimated total amount
    """
    # State-specific benefit programs and average amounts
    # These are simplified estimates - real implementation would use state APIs
    state_benefits = {
        "CA": {
            "UI": {"amount": 450, "weeks": 26},
            "SNAP": {"amount": 194, "months": 6},
            "ACA": {"amount": 350, "months": 12},
            "RETRAINING": {"amount": 5000, "one_time": True}
        },
        "NY": {
            "UI": {"amount": 504, "weeks": 26},
            "SNAP": {"amount": 194, "months": 6},
            "ACA": {"amount": 380, "months": 12},
            "RETRAINING": {"amount": 5000, "one_time": True}
        },
        "TX": {
            "UI": {"amount": 535, "weeks": 26},
            "SNAP": {"amount": 194, "months": 6},
            "ACA": {"amount": 320, "months": 12},
            "RETRAINING": {"amount": 3000, "one_time": True}
        },
        "FL": {
            "UI": {"amount": 275, "weeks": 12},
            "SNAP": {"amount": 194, "months": 6},
            "ACA": {"amount": 300, "months": 12},
            "RETRAINING": {"amount": 3000, "one_time": True}
        },
        "IL": {
            "UI": {"amount": 484, "weeks": 26},
            "SNAP": {"amount": 194, "months": 6},
            "ACA": {"amount": 360, "months": 12},
            "RETRAINING": {"amount": 5000, "one_time": True}
        }
    }
    
    state_upper = state.upper()
    
    # Default to CA if state not found
    if state_upper not in state_benefits:
        state_upper = "CA"
    
    benefits = state_benefits[state_upper]
    
    # Determine eligible programs based on post content analysis
    # In a real implementation, this would use LLM to analyze eligibility criteria
    eligible_programs = []
    total_amount = 0
    
    # Basic eligibility logic (simplified)
    # Real implementation would analyze post for work history, income, etc.
    post_lower = post_text.lower()
    
    # Unemployment Insurance - most laid-off workers qualify
    if "laid off" in post_lower or "layoff" in post_lower or "terminated" in post_lower:
        eligible_programs.append("UI")
        ui_amount = benefits["UI"]["amount"] * benefits["UI"]["weeks"]
        total_amount += ui_amount
    
    # SNAP - income-based, assume eligible if laid off
    eligible_programs.append("SNAP")
    snap_amount = benefits["SNAP"]["amount"] * benefits["SNAP"]["months"]
    total_amount += snap_amount
    
    # ACA subsidies - most qualify when unemployed
    eligible_programs.append("ACA")
    aca_amount = benefits["ACA"]["amount"] * benefits["ACA"]["months"]
    total_amount += aca_amount
    
    # Retraining vouchers - available in most states
    eligible_programs.append("RETRAINING")
    total_amount += benefits["RETRAINING"]["amount"]
    
    return {
        "programs": eligible_programs,
        "amount": round(total_amount, 2),
        "state": state_upper,
        "breakdown": {
            program: benefits[program] for program in eligible_programs
        }
    }


# Create ADK Tool wrapper
# FunctionTool automatically extracts name and description from the function docstring and signature
eligibility_engine_adk_tool = FunctionTool(eligibility_engine_tool)

