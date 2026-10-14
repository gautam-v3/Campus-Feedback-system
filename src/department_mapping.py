"""
Algorithm 6 — Department Assignment. Deliberately not ML: a lookup table
is more reliable, explainable, and correctable than a learned mapping."""
from config import DEPARTMENT_MAPPING, DEFAULT_DEPARTMENT


def assign_department(category: str) -> str:
    return DEPARTMENT_MAPPING.get(category, DEFAULT_DEPARTMENT)
