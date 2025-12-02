"""
Main entry point for Second-Chance Agent system
"""
import argparse
import sys
from agents.scout import run_scout
from agents.caseworker import run_caseworker
from agents.watchdog import run_watchdog


def main():
    parser = argparse.ArgumentParser(
        description="Second-Chance Agent - Multi-agent system for helping laid-off workers"
    )
    parser.add_argument(
        "agent",
        choices=["scout", "caseworker", "watchdog"],
        help="Which agent to run"
    )
    parser.add_argument(
        "--url",
        help="LinkedIn URL (for caseworker agent)"
    )
    parser.add_argument(
        "--all-pending",
        action="store_true",
        help="Process all pending entries (for caseworker agent)"
    )
    
    args = parser.parse_args()
    
    if args.agent == "scout":
        print("Starting Scout Agent...")
        run_scout()
    elif args.agent == "caseworker":
        print("Starting Caseworker Agent...")
        if args.url:
            from agents.caseworker import process_case
            process_case(linkedin_url=args.url)
        elif args.all_pending:
            run_caseworker()
        else:
            run_caseworker()
    elif args.agent == "watchdog":
        print("Starting Watchdog Agent...")
        run_watchdog()


if __name__ == "__main__":
    main()

