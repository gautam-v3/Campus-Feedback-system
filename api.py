"""
FastAPI backend wrapping TicketPipeline + the SQLite layer.

Run:
    uvicorn api:app --reload

Then open http://127.0.0.1:8000/  (student UI)
and    http://127.0.0.1:8000/static/staff.html  (staff UI)
"""
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from src.ticket_pipeline import TicketPipeline
from src import database
from config import VALID_STATUSES, DEPARTMENT_MAPPING, DEFAULT_DEPARTMENT

app = FastAPI(title="Campus Maintenance Intelligence System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline: Optional[TicketPipeline] = None


@app.on_event("startup")
def startup():
    global pipeline
    database.init_db()
    pipeline = TicketPipeline()


class ComplaintIn(BaseModel):
    registration_number: str
    complaint_text: str


class StatusUpdateIn(BaseModel):
    status: str


@app.post("/api/complaints")
def submit_complaint(payload: ComplaintIn):
    """Steps 2-14: student submits a complaint, full pipeline runs, ticket stored."""
    if not payload.complaint_text.strip():
        raise HTTPException(status_code=400, detail="complaint_text cannot be empty")
    ticket = pipeline.process_complaint(
        payload.complaint_text, student_id=payload.registration_number
    )
    return ticket


@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    """Step 17-18: retrieve by Complaint ID."""
    complaint = database.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.get("/api/complaints/by-registration/{registration_number}")
def get_complaints_for_student(registration_number: str):
    """Step 17-18: retrieve by Registration Number."""
    return database.get_complaints_by_registration(registration_number)


@app.get("/api/departments")
def list_departments():
    return sorted(set(DEPARTMENT_MAPPING.values()) | {DEFAULT_DEPARTMENT})


@app.get("/api/departments/{department}/complaints")
def get_complaints_for_department(department: str):
    return database.get_complaints_by_department(department)


@app.get("/api/priorities")
def list_priorities():
    priorities = database.get_distinct_priorities()
    return priorities if priorities else ["Critical", "High", "Medium", "Low"]


@app.get("/api/complaints")
def list_all_complaints():
    return database.get_all_complaints()


@app.patch("/api/complaints/{complaint_id}/status")
def update_status(complaint_id: str, payload: StatusUpdateIn):
    """Step 15-16: staff updates status."""
    if payload.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {VALID_STATUSES}",
        )
    if not database.get_complaint(complaint_id):
        raise HTTPException(status_code=404, detail="Complaint not found")

    updated = database.update_status(complaint_id, payload.status)
    return updated


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
