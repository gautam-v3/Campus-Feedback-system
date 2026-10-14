"""
Notification service — deliberately decoupled from the decision engine
(see design doc section 14). This stub prints/logs; swap in real email/
push logic later without touching ticket_pipeline.py.
"""


def notify_department(ticket: dict) -> None:
    print(
        f"[NOTIFY] New {ticket['final_priority']} priority complaint "
        f"{ticket['ticket_id']} routed to {ticket['assigned_department']}"
    )
    if ticket.get("safety_rule_escalated"):
        print(f"  -> Escalated by safety rules (matched: {ticket['matched_safety_keywords']})")


def notify_student_status_change(ticket_id: str, student_id: str, new_status: str) -> None:
    print(f"[NOTIFY] Student {student_id}: your complaint {ticket_id} is now '{new_status}'")
