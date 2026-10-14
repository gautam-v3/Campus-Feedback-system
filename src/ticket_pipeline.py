"""
Full complaint processing pipeline:

Complaint
    ↓
NLP preprocessing
    ↓
NER
    ↓
Category SVM
    ↓
Priority SVM
    ↓
Safety / Severity Rules
    ↓
Safety Category Override
    ↓
Department Assignment
    ↓
SQLite Database
    ↓
Notification
"""

import uuid
import joblib
from datetime import datetime, timezone

from config import (
    CATEGORY_MODEL_PATH,
    CATEGORY_VECTORIZER_PATH,
    PRIORITY_MODEL_PATH,
    PRIORITY_VECTORIZER_PATH,
)

from src.preprocessing import preprocess_text

from src.safety_rules import (
    apply_safety_rules,
    get_safety_category,
)

from src.department_mapping import assign_department
from src.ner_pipeline import load_ner_pipeline, extract_entities
from src.notification_service import notify_department
from src import database


class TicketPipeline:

    def __init__(self):
        print("Loading trained artifacts...")

        self.category_model = joblib.load(CATEGORY_MODEL_PATH)
        self.category_vectorizer = joblib.load(CATEGORY_VECTORIZER_PATH)

        self.priority_model = joblib.load(PRIORITY_MODEL_PATH)
        self.priority_vectorizer = joblib.load(PRIORITY_VECTORIZER_PATH)

        self.nlp = load_ner_pipeline()

        database.init_db()

        print("All artifacts loaded. Database ready.")

    def process_complaint(
        self,
        complaint_text: str,
        student_id: str = "unknown"
    ) -> dict:

        # --------------------------------------------------
        # 1. NLP PREPROCESSING
        # --------------------------------------------------
        clean_text = preprocess_text(complaint_text)

        # --------------------------------------------------
        # 2. NER
        # --------------------------------------------------
        entities = extract_entities(
            self.nlp,
            complaint_text
        )

        # --------------------------------------------------
        # 3. CATEGORY SVM
        # --------------------------------------------------
        category_vec = self.category_vectorizer.transform(
            [clean_text]
        )

        category = self.category_model.predict(
            category_vec
        )[0]

        # --------------------------------------------------
        # 4. PRIORITY SVM
        # --------------------------------------------------
        priority_vec = self.priority_vectorizer.transform(
            [clean_text]
        )

        ml_priority = self.priority_model.predict(
            priority_vec
        )[0]

        # --------------------------------------------------
        # 5. SAFETY / SEVERITY RULES
        # --------------------------------------------------
        final_priority, escalated, matched_keywords = apply_safety_rules(
            complaint_text,
            ml_priority
        )

        # --------------------------------------------------
        # 6. SAFETY CATEGORY OVERRIDE
        # --------------------------------------------------
        # Example:
        # "electric shock" → Electrical
        # even if the SVM incorrectly predicts Cleaning.

        safety_category = get_safety_category(
            complaint_text
        )

        if safety_category is not None:
            category = safety_category

        # --------------------------------------------------
        # 7. DEPARTMENT ASSIGNMENT
        # --------------------------------------------------
        department = assign_department(category)

        # --------------------------------------------------
        # 8. CREATE TICKET
        # --------------------------------------------------
        ticket = {
            "ticket_id": f"CMP-{uuid.uuid4().hex[:8].upper()}",

            "student_id": student_id,

            "complaint_text": complaint_text,

            "clean_text": clean_text,

            "entities": entities,

            "category": category,

            "ml_priority": ml_priority,

            "final_priority": final_priority,

            "safety_rule_escalated": escalated,

            "matched_safety_keywords": matched_keywords,

            "assigned_department": department,

            "status": "Submitted",

            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        # --------------------------------------------------
        # 9. STORE COMPLAINT IN SQLITE
        # --------------------------------------------------
        database.create_complaint(ticket)

        # --------------------------------------------------
        # 10. CREATE NOTIFICATION
        # --------------------------------------------------
        message = (
            f"New {final_priority} priority complaint "
            f"{ticket['ticket_id']} "
            f"({category}) awaiting action."
        )

        database.create_notification(
            ticket["ticket_id"],
            department,
            message
        )

        # --------------------------------------------------
        # 11. NOTIFY DEPARTMENT
        # --------------------------------------------------
        notify_department(ticket)

        return ticket


if __name__ == "__main__":

    pipeline = TicketPipeline()

    test_complaints = [

        "The projector in Lab 5 isn't working and we have a presentation tomorrow",

        "There is a dangerous exposed live wire near the hostel stairs",

        "I got an electric shock from the switchboard",

        "Wi-Fi is very slow in the library",

    ]

    for text in test_complaints:

        ticket = pipeline.process_complaint(
            text,
            student_id="S12345"
        )

        print("\n" + "=" * 60)

        for key, value in ticket.items():
            print(f"{key}: {value}")