"""
Central configuration: paths, department mapping, safety keywords.
Edit this file rather than hunting through the pipeline code.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

RAW_CSV_PATH = os.path.join(DATA_DIR, "complaints.csv")
PROCESSED_CSV_PATH = os.path.join(DATA_DIR, "complaints_processed.csv")

CATEGORY_MODEL_PATH = os.path.join(MODELS_DIR, "category_svm_model.pkl")
CATEGORY_VECTORIZER_PATH = os.path.join(MODELS_DIR, "category_tfidf_vectorizer.pkl")
PRIORITY_MODEL_PATH = os.path.join(MODELS_DIR, "priority_svm_model.pkl")
PRIORITY_VECTORIZER_PATH = os.path.join(MODELS_DIR, "priority_tfidf_vectorizer.pkl")
NER_MODEL_PATH = os.path.join(MODELS_DIR, "campus_ner_model")

DB_PATH = os.path.join(DATA_DIR, "campus_maintenance.db")

VALID_STATUSES = ["Submitted", "Assigned", "In Progress", "Resolved"]

# category -> department mapping (Algorithm 6 from the design doc)
DEPARTMENT_MAPPING = {
    "Electrical": "Electrical Maintenance",
    "Plumbing": "Plumbing Maintenance",
    "Network": "IT Department",
    "Classroom Equipment": "AV / IT Support",
    "Infrastructure": "Civil Maintenance",
    "Cleaning": "Housekeeping",
    "Safety": "Security / Safety Team",
}
DEFAULT_DEPARTMENT = "General Maintenance"

# Rule layer keywords -> force Critical regardless of what the SVM predicts.
# Expand this list once you've inspected real complaint text from your campus.
CRITICAL_KEYWORDS = [
    "fire", "smoke", "electric shock", "shock", "exposed wire",
    "exposed live wire", "live wire", "spark", "sparks", "sparking",
    "collapse", "collapsed", "ceiling fell", "ceiling collapsed",
    "injured", "injury", "gas leak", "gas smell", "burning smell",
    "flood", "flooding", "dangerous", "unsafe", "electrocuted",
]

# NER pattern vocab — expand with real campus block/equipment names
EQUIPMENT_TERMS = [
    "projector", "ac", "air conditioner", "fan", "light", "bulb",
    "wifi", "wi-fi", "router", "computer", "printer", "chair",
    "desk", "door", "window", "tap", "pipe", "switchboard", "socket",
]
BLOCK_TERMS = [
    "block a", "block b", "block c", "ab block", "cd block",
    "main block", "hostel block", "academic block",
]
PROBLEM_TERMS = [
    "not working", "broken", "damaged", "leaking", "not cooling",
    "slow", "stopped working", "not turning on", "flickering",
    "cracked", "stuck", "blocked", "overflowing",
]

DUPLICATE_SIMILARITY_THRESHOLD = 0.80
