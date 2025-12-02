"""
Test script for Second-Chance Agent components
"""
import os
from dotenv import load_dotenv
from tools.eligibility_engine import eligibility_engine_tool
from utils.shared_state import append_to_shared_state, get_statistics, read_shared_state

load_dotenv()


def test_eligibility_engine():
    """Test the eligibility engine tool"""
    print("Testing Eligibility Engine...")
    
    test_cases = [
        ("CA", "I was laid off from my job at Tech Corp after 5 years. Looking for new opportunities."),
        ("NY", "Unfortunately, I've been terminated from my position. Open to work!"),
        ("TX", "Laid off today. Time to find something new."),
    ]
    
    for state, post_text in test_cases:
        result = eligibility_engine_tool(state, post_text)
        print(f"\nState: {state}")
        print(f"Post: {post_text[:50]}...")
        print(f"Eligible Programs: {result['programs']}")
        print(f"Estimated Amount: ${result['amount']:,.2f}")


def test_shared_state():
    """Test shared state management"""
    print("\n\nTesting Shared State Management...")
    
    # Add test entry
    test_entry = {
        "linkedin_url": "https://www.linkedin.com/posts/test123",
        "state": "CA",
        "post_text": "Test post about being laid off",
        "title": "Test Post",
        "status": "pending"
    }
    
    if append_to_shared_state(test_entry):
        print("✓ Successfully appended test entry")
    
    # Read entries
    entries = read_shared_state()
    print(f"✓ Total entries: {len(entries)}")
    
    # Get statistics
    stats = get_statistics()
    print(f"✓ Total amount unlocked: ${stats['total_amount_unlocked']:,.2f}")
    print(f"✓ Total rows: {stats['total_rows']}")


def test_state_extraction():
    """Test state extraction from text"""
    print("\n\nTesting State Extraction...")
    
    from agents.scout import extract_state_from_text
    
    test_texts = [
        "I was laid off from my job in California",
        "Based in New York, looking for work",
        "Located in TX, open to opportunities",
        "From Florida, recently terminated"
    ]
    
    for text in test_texts:
        state = extract_state_from_text(text)
        print(f"Text: {text}")
        print(f"Extracted State: {state}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Second-Chance Agent - Component Tests")
    print("=" * 60)
    
    test_eligibility_engine()
    test_shared_state()
    test_state_extraction()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

