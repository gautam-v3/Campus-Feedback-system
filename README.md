# Campus Maintenance Intelligence System

An NLP-powered campus maintenance complaint management system that classifies student complaints, predicts their priority, identifies relevant entities and locations, applies safety escalation rules, and routes complaints to the appropriate maintenance department.

## Overview

The Campus Maintenance Intelligence System streamlines the handling of campus maintenance complaints through Natural Language Processing (NLP) and Machine Learning (ML).

Students can submit complaints through a web interface. The system processes the complaint, predicts its category and priority, applies rule-based safety checks, assigns a responsible department, and stores the resulting ticket in an SQLite database.

The application provides a student-facing interface, a staff interface for managing assigned complaints, a REST API, and command-line tools for training and testing the NLP pipeline.

### Key Features

- **Complaint classification:** Uses TF-IDF features and a Support Vector Machine (SVM) to predict complaint categories.
- **Priority prediction:** Uses a separate TF-IDF and SVM pipeline to estimate complaint priority.
- **Named Entity Recognition:** Uses a custom spaCy pipeline to identify relevant entities and locations.
- **Safety escalation:** Applies rule-based checks to escalate complaints containing configured safety hazards to Critical priority.
- **Department assignment:** Maps complaint categories to the appropriate maintenance department.
- **Ticket management:** Stores complaints, ticket information, and notification records in SQLite.
- **Web interface:** Provides student complaint submission and tracking, along with a staff queue and status updates.
- **REST API:** Exposes endpoints for submitting complaints, retrieving tickets, listing departments, and updating complaint status.
- **Model training and inference:** Supports both command-line execution and web-based operation.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Backend and REST API | FastAPI |
| ASGI server | Uvicorn |
| NLP and entity extraction | spaCy |
| Text feature extraction | TF-IDF |
| Machine learning | scikit-learn, SVM |
| Data storage | SQLite |
| Data processing | pandas |
| Frontend | HTML, CSS, JavaScript |
| Model persistence | Joblib / Python serialized model artifacts |

## System Architecture

```text
Student / Staff
       |
       v
HTML, CSS and JavaScript Interface
       |
       v
FastAPI Application
       |
       v
Complaint Processing Pipeline
       |
       +--> Text preprocessing
       |
       +--> Named Entity Recognition
       |
       +--> Category classification (SVM)
       |
       +--> Priority prediction (SVM)
       |
       +--> Safety escalation rules
       |
       +--> Department assignment
       |
       v
Ticket and Notification Records
       |
       v
SQLite Database
```

The system uses machine-learning predictions together with explicit safety rules. The safety rules can override the model's predicted priority when configured hazard keywords are detected.

## Project Structure

```text
Campus-Feedback-system/
|
|-- api.py
|-- config.py
|-- main_train.py
|-- main_infer.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|
|-- src/
|   |-- __init__.py
|   |-- preprocessing.py
|   |-- train_models.py
|   |-- ner_pipeline.py
|   |-- safety_rules.py
|   |-- department_mapping.py
|   |-- ticket_pipeline.py
|   |-- notification_service.py
|   |-- database.py
|
|-- static/
|   |-- index.html
|   |-- staff.html
|   |-- admin.html
|
|-- data/
|   |-- complaints.csv             # Supply your own training dataset
|   |-- campus_maintenance.db     # Created locally at runtime
|
|-- models/
    |-- category_svm_model.pkl
    |-- category_tfidf_vectorizer.pkl
    |-- priority_svm_model.pkl
    |-- priority_tfidf_vectorizer.pkl
    |-- campus_ner_model/
    |-- category_confusion_matrix.png
    |-- priority_confusion_matrix.png
```

The tree shows the expected structure. Actual generated files may differ depending on the repository version and whether models have already been trained.

## Prerequisites

Install the following before running the application:

- Python 3.11 or another Python version compatible with the dependencies in `requirements.txt`.
- Git, if cloning the repository.
- A web browser.
- Internet access during initial dependency and spaCy language-model installation.

Check your installed Python version:

```powershell
python --version
```

## Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/gautam-v3/Campus-Feedback-system.git
cd Campus-Feedback-system
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks virtual-environment activation, you can use the environment's Python executable directly or adjust your PowerShell execution policy according to your system's security requirements.

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Install the spaCy English model

```powershell
python -m spacy download en_core_web_sm
```

The custom campus NER pipeline and the English language model are separate dependencies. Install the English model if the project's code requires it.

### 5. Prepare the training dataset

The training dataset is not guaranteed to be included in the public repository. Create `data/complaints.csv` and provide your own dataset.

The training CSV must contain these columns:

| Column | Description |
|---|---|
| `complaint_text` | Text describing the maintenance issue |
| `category` | Target category for the complaint |
| `priority` | Target priority label |

Example structure:

```csv
complaint_text,category,priority
"The projector in Lab 5 is not working",Classroom Equipment,Medium
"Water is leaking from the washroom tap",Plumbing,Low
"Sparks are coming from an electrical panel",Electrical,Critical
```

These rows illustrate the expected format only. Use appropriately labeled, representative data for meaningful model training.

Ensure the category and priority labels are consistent with the labels and mappings expected by the project's configuration and training code.

## Training the Models

To train the category classifier, priority classifier, and custom NER pipeline, run:

```powershell
python main_train.py
```

The training workflow is intended to:

1. Load the complaint dataset.
2. Preprocess complaint text.
3. Extract TF-IDF features.
4. Train the category SVM classifier.
5. Train the priority SVM classifier.
6. Evaluate the classifiers and generate confusion-matrix plots.
7. Build and save the custom spaCy NER pipeline.
8. Save the trained model artifacts under `models/`.

Training output depends on the dataset, labels, train/test split, and configuration.

**Important:** Do not retrain the models merely to run inference if the required trained artifacts are already available and compatible with the installed libraries.

## Running Command-Line Inference

Run the interactive inference program:

```powershell
python main_infer.py
```

To process a single complaint:

```powershell
python main_infer.py "The projector in Lab 5 is not working"
```

The pipeline is designed to process the complaint, predict its category and priority, apply safety rules, determine the department, and produce a ticket result.

Example complaints to test:

```text
The projector in G05 is not working.
Water is leaking near the washroom.
Sparks are coming from the electrical panel near Room 112.
The classroom ceiling has visible cracks.
```

The predicted result depends on the trained models, entity extraction rules, department mappings, and configured safety keywords.

## Running the Web Application

Start the FastAPI server from the project root:

```powershell
python -m uvicorn api:app --reload
```

Once the server starts, open these URLs in your browser.

| Interface | URL |
|---|---|
| Student interface | http://127.0.0.1:8000/ |
| Staff interface | http://127.0.0.1:8000/static/staff.html |
| Admin interface | http://127.0.0.1:8000/static/admin.html |
| Interactive API documentation | http://127.0.0.1:8000/docs |
| Alternative API documentation | http://127.0.0.1:8000/redoc |

The admin interface is included in the frontend, but the availability of specific administrative operations depends on the implemented backend routes.

Keep the terminal open while using the application. To stop the server, press `Ctrl+C`.

## REST API

The following endpoints are documented by the project.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/complaints` | Submit a complaint and process it through the pipeline |
| `GET` | `/api/complaints/{complaint_id}` | Retrieve a complaint by ticket ID |
| `GET` | `/api/complaints/by-registration/{reg_no}` | Retrieve complaints associated with a registration number |
| `GET` | `/api/departments` | List departments |
| `GET` | `/api/departments/{department}/complaints` | Retrieve complaints assigned to a department |
| `PATCH` | `/api/complaints/{complaint_id}/status` | Update a complaint's status |

For request schemas, response formats, and interactive testing, start the application and visit:

http://127.0.0.1:8000/docs

### Complaint Processing Workflow

A complaint submitted through the API follows the intended workflow:

1. Receive the complaint text and relevant student information.
2. Preprocess the complaint text.
3. Extract relevant entities and locations using the NLP pipeline.
4. Predict the complaint category using the category classifier.
5. Predict priority using the priority classifier.
6. Apply configured safety rules and escalation overrides.
7. Map the final category to a responsible department.
8. Store the complaint and create a notification record.
9. Return the ticket information to the client.

The exact response fields and behavior depend on the current implementation.

## Safety and Priority Escalation

The priority classifier estimates priority from learned text patterns. Rule-based safety checks provide an additional layer for configured hazard keywords.

For example, a complaint containing a configured electrical hazard term may be escalated to Critical priority even if the machine-learning model predicts a lower priority.

Safety rules are keyword-based, not a complete understanding of physical risk. They can miss unfamiliar wording or trigger on a keyword used in a non-hazardous context. They must not be treated as a replacement for human assessment or emergency procedures.

## Database

The application uses SQLite to store complaint and notification records.

The database is configured through the project's configuration and database modules. During application startup, the backend initializes the database schema if necessary.

The local database is intended for development and demonstration. A fresh installation may not contain historical complaints, and users should not expect another developer's local database to be included in the repository.

## Notification Handling

The project includes a notification service and creates notification records as part of the complaint workflow. Actual email, SMS, or push delivery depends on the implementation and configuration of the notification service; do not assume external notifications are delivered unless a real provider has been integrated and tested.

## Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and reinstall the requirements:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### spaCy model not found

Install the English language model:

```powershell
python -m spacy download en_core_web_sm
```

### Trained model file not found

Check that the expected model files exist under `models/`. If they are missing, train the models using a valid dataset:

```powershell
python main_train.py
```

### Dataset not found

Ensure `data/complaints.csv` exists and contains the required `complaint_text`, `category`, and `priority` columns.

### Port 8000 is already in use

Start the application on another port:

```powershell
python -m uvicorn api:app --reload --port 8001
```

Then open `http://127.0.0.1:8001/docs`.

## Current Limitations

- Classification quality depends on the size, quality, and representativeness of the training dataset.
- Priority predictions are estimates and should be evaluated against representative data.
- Safety escalation relies on configured keywords and is not a complete hazard-detection system.
- Authentication and role-based access control are not implemented as production-grade security controls.
- The notification service may record notifications without delivering real external messages.
- Duplicate complaint detection is not implemented.
- The project is intended as an academic prototype, not as a production-ready campus emergency response platform.

## Future Improvements

Potential future work includes:

- Improve and evaluate model performance using a larger, more diverse, accurately labeled dataset.
- Expand location recognition for campus-specific room and building formats.
- Add secure authentication and authorization.
- Integrate a real notification provider.
- Implement duplicate detection for open complaints.
- Improve monitoring, audit logging, and administrative reporting.
- Add automated tests for API routes, NLP predictions, and safety escalation rules.

These are proposed improvements and should not be considered implemented features.

## Privacy and Security

Do not commit real student registration numbers, personally identifiable complaint records, database files containing private data, credentials, API keys, or other secrets to a public repository.

Use anonymized or synthetic data for demonstrations. Review `.gitignore` before committing new files, and remember that adding a file to `.gitignore` does not remove it if it is already tracked by Git.

## License

No license is specified in this repository at present. Unless a license is added, others should not assume they have permission to reuse, distribute, or modify the project beyond the rights granted by applicable law.

## Author

**Gautam V.**

GitHub: [@gautam-v3](https://github.com/gautam-v3)

Repository: [Campus-Feedback-system](https://github.com/gautam-v3/Campus-Feedback-system)