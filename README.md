# Campus Maintenance Intelligence System — VS Code Project

Local pipeline (no Colab/manual uploads). Replace `data/complaints.csv`
with your own dataset (a 15-row placeholder is included so the project
runs immediately for a sanity check).

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 1. Add your dataset

Replace `data/complaints.csv`. Required columns:
- `complaint_text`
- `category`
- `priority`

## 2. Train

```bash
python main_train.py
```

This runs preprocessing, trains the Category SVM and Priority SVM,
saves confusion matrix plots, builds the NER pipeline, and saves
everything into `models/`.

## 3. Run the decision engine

Interactive:
```bash
python main_infer.py
```

Single complaint:
```bash
python main_infer.py "The projector in Lab 5 isn't working"
```

Each call runs the full pipeline and prints a ticket as JSON:

```
Complaint
  -> NER + NLP preprocessing
  -> Category SVM
  -> Priority SVM
  -> Safety/Severity Rules   (can force priority to Critical)
  -> Final Priority
  -> Department Assignment
  -> Ticket created
  -> Department notified
```

## Project structure

```
config.py                    # paths, department mapping, safety keywords, NER vocab
main_train.py                 # entry point: train everything
main_infer.py                 # entry point: run the decision engine
src/
  preprocessing.py            # negation-safe text cleaning
  train_models.py              # category + priority SVM training/eval
  ner_pipeline.py               # spaCy EntityRuler build/save/load
  safety_rules.py                # keyword-based Critical escalation
  department_mapping.py           # category -> department lookup
  ticket_pipeline.py               # the full decision engine (TicketPipeline class)
  notification_service.py           # notification stub (swap in real email/push later)
data/complaints.csv                  # your dataset goes here
models/                                # trained artifacts land here after training
```

## Notes on the priority model

The Priority SVM is expected to be imperfect (~80-90% is a healthy target,
not 100%) — it's handling the ambiguous middle ground (Low/Medium/High).
It is NOT the safety guarantee. `src/safety_rules.py` sits on top of it and
forces `Critical` whenever a hazard keyword appears (fire, exposed wire,
gas leak, etc.), regardless of what the SVM predicted. Expand the keyword
list in `config.py` as you find more real hazard phrasing in your data.

## 4. Run the API + UI

```bash
uvicorn api:app --reload
```

Then open:
- **Student UI:** http://127.0.0.1:8000/ — submit a complaint, track by registration number
- **Staff UI:** http://127.0.0.1:8000/static/staff.html — pick a department, view its complaints, update status (Submitted → Assigned → In Progress → Resolved)

On first startup, `api.py` calls `database.init_db()` and creates
`data/campus_maintenance.db` (SQLite) with two tables: `complaints` and
`notifications`, matching the database algorithm exactly (steps 10-18).

### API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/complaints` | Submit a complaint — runs the full decision engine, stores the ticket, creates a notification |
| GET | `/api/complaints/{complaint_id}` | Retrieve one complaint by ticket ID |
| GET | `/api/complaints/by-registration/{reg_no}` | Retrieve all complaints for a student |
| GET | `/api/departments` | List all departments |
| GET | `/api/departments/{department}/complaints` | List complaints assigned to a department |
| PATCH | `/api/complaints/{complaint_id}/status` | Staff updates status (sets `resolved_at` automatically when status = Resolved) |

You can also still use `main_infer.py` directly from the terminal without
the API — it uses the same `TicketPipeline` and writes to the same
SQLite database.

## Next steps not yet included

- Duplicate complaint detection (TF-IDF + cosine similarity across
  existing open tickets)
- Authentication (currently anyone can submit/update — fine for a college
  project demo, not for real deployment)
- Analytics dashboard for admins (the raw data is already in SQLite —
  `SELECT category, COUNT(*) FROM complaints GROUP BY category` etc.)
