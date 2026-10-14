"""
NER: spaCy base model + rule-based EntityRuler for VIT Vellore campus
vocabulary and room/location patterns.

Recognizes:
    G01 - G24       -> Ground floor rooms
    101 - 124       -> 1st floor rooms
    201 - 224       -> 2nd floor rooms
    301 - 324       -> 3rd floor rooms
    ...
    Lab G05
    Room G05
    Lab 112
    Room 112

Entities:
    EQUIPMENT
    LOCATION
    BLOCK
    PROBLEM
"""

import os
import spacy

from config import (
    NER_MODEL_PATH,
    EQUIPMENT_TERMS,
    BLOCK_TERMS,
    PROBLEM_TERMS,
)


# ---------------------------------------------------------
# VIT VELLORE ROOM PATTERNS
# ---------------------------------------------------------

# Ground floor:
# G01 ... G24
GROUND_ROOM_REGEX = r"^[Gg](0[1-9]|1[0-9]|2[0-4])$"

# Upper floors:
# 101 ... 124
# 201 ... 224
# 301 ... 324
# etc.
UPPER_FLOOR_ROOM_REGEX = r"^[1-9](0[1-9]|1[0-9]|2[0-4])$"


def build_ner_pipeline():
    """Build a fresh spaCy pipeline with campus-specific EntityRuler patterns."""

    nlp = spacy.load("en_core_web_sm")

    # Remove an existing ruler if this function is ever called
    # on a pipeline that already contains one.
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")

    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = []

    # -----------------------------------------------------
    # EQUIPMENT
    # -----------------------------------------------------

    for term in EQUIPMENT_TERMS:
        patterns.append({
            "label": "EQUIPMENT",
            "pattern": term
        })

    # -----------------------------------------------------
    # BLOCK
    # -----------------------------------------------------

    for term in BLOCK_TERMS:
        patterns.append({
            "label": "BLOCK",
            "pattern": term
        })

    # -----------------------------------------------------
    # PROBLEM
    # -----------------------------------------------------

    for term in PROBLEM_TERMS:
        patterns.append({
            "label": "PROBLEM",
            "pattern": term
        })

    # -----------------------------------------------------
    # LOCATION - VIT ROOM NUMBERS
    # -----------------------------------------------------

    # G01 ... G24
    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {
                "TEXT": {
                    "REGEX": GROUND_ROOM_REGEX
                }
            }
        ]
    })

    # 101 ... 124
    # 201 ... 224
    # 301 ... 324
    # etc.
    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {
                "TEXT": {
                    "REGEX": UPPER_FLOOR_ROOM_REGEX
                }
            }
        ]
    })

    # -----------------------------------------------------
    # LOCATION - "LAB G05", "ROOM 112", etc.
    # -----------------------------------------------------

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "lab"},
            {
                "TEXT": {
                    "REGEX": GROUND_ROOM_REGEX
                }
            }
        ]
    })

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "lab"},
            {
                "TEXT": {
                    "REGEX": UPPER_FLOOR_ROOM_REGEX
                }
            }
        ]
    })

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "room"},
            {
                "TEXT": {
                    "REGEX": GROUND_ROOM_REGEX
                }
            }
        ]
    })

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "room"},
            {
                "TEXT": {
                    "REGEX": UPPER_FLOOR_ROOM_REGEX
                }
            }
        ]
    })

    # Existing campus patterns
    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "lab"},
            {"IS_DIGIT": True}
        ]
    })

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "room"},
            {"IS_DIGIT": True}
        ]
    })

    patterns.append({
        "label": "LOCATION",
        "pattern": [
            {"LOWER": "hostel"},
            {"IS_DIGIT": True, "OP": "?"}
        ]
    })

    ruler.add_patterns(patterns)

    return nlp


def save_ner_pipeline(nlp, path: str = NER_MODEL_PATH):
    """Save the complete NER pipeline."""
    nlp.to_disk(path)


def load_ner_pipeline(path: str = NER_MODEL_PATH):
    """Load saved NER pipeline or build a fresh one if unavailable."""

    if os.path.exists(path):
        return spacy.load(path)

    return build_ner_pipeline()


def extract_entities(nlp, text: str) -> dict:
    """Extract campus-specific entities from complaint text."""

    doc = nlp(text)

    entities = {
        "EQUIPMENT": [],
        "LOCATION": [],
        "BLOCK": [],
        "PROBLEM": []
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    return entities


if __name__ == "__main__":

    nlp = build_ner_pipeline()
    save_ner_pipeline(nlp)

    print(f"NER pipeline saved to {NER_MODEL_PATH}")

    test_texts = [
        "The projector in G05 is not working",
        "The projector in Lab G05 is not working",
        "The AC in room 112 is not cooling",
        "The fan in Room 204 is broken",
        "The light in G24 is flickering",
        "The projector in Lab 112 is not working",
        "There is a problem in Block C room 215",
        "The computer in 324 is not working",
    ]

    for text in test_texts:
        print("\nComplaint:", text)
        print("Entities:", extract_entities(nlp, text))