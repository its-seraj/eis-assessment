# School Application Project

This project is a full-stack web application designed to manage and view student marks. It consists of a Django backend providing a RESTful API and a React frontend built with Vite.

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
- **Python 3.x** (for the Django backend)
- **Node.js** (for the React/Vite frontend)

## Setup Instructions

### Backend (Django)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended).
3. Install dependencies (assuming `django` and `djangorestframework` are required):
   ```bash
   pip install django djangorestframework
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```
   The backend will be available at `http://127.0.0.1:8000/`.

### Frontend (React + Vite)

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173/` (or the port specified by Vite).

## Data Management

### 1. Data Ingestion (CSV Import)
To populate the database initially with students and their marks, a custom Django management command is provided. This command reads from a CSV file (e.g., `students_marks.csv`), clears any existing data, and bulk-inserts the new records for efficiency.

Run the following command from the `backend` directory, providing the path to your CSV file:
```bash
python manage.py import_marks ../students_marks.csv
```

### 2. Applying Data Corrections
If marks need to be updated after the initial ingestion, you can use the corrections API route (`POST /api/marks/corrections/`). A helper script `apply_corrections.py` is provided to automate this process using a JSON file (`corrections.json`).

To apply the corrections:
1. Ensure your Django server is running.
2. Ensure the `corrections.json` file is populated with the desired updates (formatted with `admission_no`, `subject`, and `marks`).
3. Run the script from the `backend` directory:
   ```bash
   python apply_corrections.py
   ```
This script will iterate through the JSON file and make HTTP POST requests to the corrections route to update the database securely.

## API Routes and Responses

The backend provides the following REST API endpoints:

### 1. Student List
- **Route:** `GET /api/students/`
- **Query Parameters:** `?search=<name>` (optional, to filter students by name)
- **Response:** A JSON array of student objects containing their basic details.

### 2. Student Detail
- **Route:** `GET /api/students/<admission_no>/`
- **Response:** A JSON object detailing a specific student, including their marks in all subjects.

### 3. Summary Statistics
- **Route:** `GET /api/summary/`
- **Response:** A JSON object containing overall class statistics:
  - `subject_stats`: A dictionary grouping by subject, providing the `average` marks and a list of `top_students` (up to 5) for that subject.
  - `top_student`: Details of the single student with the highest total marks across all subjects.
  - `top_5_students`: Details of the top 5 students overall based on total marks.

### 4. Marks Corrections
- **Route:** `POST /api/marks/corrections/`
- **Payload:** JSON body with `admission_no`, `subject`, and `marks`.
- **Response:** `{"status": "success"}` on successful update or creation, or `400 Bad Request` with errors if invalid.

**Example `curl` request:**
```bash
curl -X POST http://127.0.0.1:8000/api/marks/corrections/ \
     -H "Content-Type: application/json" \
     -d '{"admission_no": "12345", "subject": "Mathematics", "marks": 95}'
```

## Logic and Queries Explained

### Summary Data Calculation
The summary endpoint uses Django's ORM aggregation and annotation features for efficient database querying:
- **Subject Averages:** Uses `Avg('marks_obtained')` grouped by subject to calculate the class average per subject.
- **Top 5 Students (Per Subject):** Filters marks by subject and uses `order_by('-marks_obtained')[:5]` to get the highest scoring students efficiently.
- **Top Students (Overall):** Uses `annotate(total_marks=Sum('marks__marks_obtained'))` on the `Student` model to dynamically calculate each student's total marks, and then orders them descending to pick the top 5.

### Marks Update Logic
The corrections endpoint uses `get_or_create` on the `SubjectMark` model. This logic allows updating existing mark records or creating new ones seamlessly without duplicating data for a specific student and subject combination.

## Additional Features Added

- **Hover to Show Top 5 Students:** On the frontend summary page, a dynamic hover interaction has been added. Hovering over a specific element reveals the top 5 students, enhancing the user experience by providing quick insights without needing to navigate away or click.

## Video Demo

You can watch a quick demonstration of the application in action here:
[Loom Video Demo](https://www.loom.com/share/3e5f3e7bf0304075888cd9e15c321dc8)
