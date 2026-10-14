"""
Entry point: run the full decision engine on complaints.

Interactive usage:
    python main_infer.py

Single complaint usage:
    python main_infer.py "The projector in Lab 5 isn't working"
"""
import sys
import json
from src.ticket_pipeline import TicketPipeline


def main():
    pipeline = TicketPipeline()

    if len(sys.argv) > 1:
        complaint_text = " ".join(sys.argv[1:])
        ticket = pipeline.process_complaint(complaint_text)
        print("\n" + json.dumps(ticket, indent=2, default=str))
        return

    print("\nEnter a complaint (or 'quit' to exit):")
    while True:
        text = input("> ").strip()
        if text.lower() in ("quit", "exit"):
            break
        if not text:
            continue
        ticket = pipeline.process_complaint(text)
        print(json.dumps(ticket, indent=2, default=str))
        print()


if __name__ == "__main__":
    main()
