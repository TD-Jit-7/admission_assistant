from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
import json
from database import get_db, Student

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini AI
GEMINI_API_KEY = "AIzaSyCoZd1akvhUZViGcmfTkOlL10HsnhUVJJo"
client = genai.Client(api_key=GEMINI_API_KEY)
# Load university data from JSON file
with open('universities.json', 'r', encoding='utf-8') as f:
    universities = json.load(f)

# Request models
class ChatRequest(BaseModel):
    message: str
    student_id: int = None

class StudentData(BaseModel):
    name: str = None
    academic_group: str = None
    gpa: float = None
    interested_department: str = None
    preferred_university_type: str = None

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "University Admission Assistant API",
        "status": "running",
        "total_universities": len(universities)
    }

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message
    
    # Get student data if student_id is provided
    student_context = ""
    if request.student_id:
        student = db.query(Student).filter(Student.id == request.student_id).first()
        if student:
            student_context = f"""
            Student Profile:
            - Name: {student.name}
            - Academic Group: {student.academic_group}
            - GPA: {student.gpa}
            - Interested Department: {student.interested_department}
            - Preferred University Type: {student.preferred_university_type}
            """
    
    # Create system prompt with university data
    system_prompt = f"""You are a helpful AI admission assistant for Bangladeshi students looking for university guidance.

Available Universities in Bangladesh:
{json.dumps(universities, indent=2)}

{student_context}

Your responsibilities:
1. Help students find suitable universities based on their academic profile
2. Recommend universities that match their GPA, department preference, and university type
3. Inform them about admission status (Open/Closed)
4. If you don't have information about their GPA, academic group, or department preference, politely ask for it
5. Be friendly, encouraging, and helpful
6. Provide specific recommendations with reasons

Important:
- Only recommend universities where admission_status is "Open"
- Only recommend universities where the student's GPA meets the minimum_gpa requirement
- If a student asks about a department, show all universities offering that department
- If a student asks about public/private universities, filter accordingly

Answer the student's question based on the available university data."""

    try:
        # Generate response using Gemini
        full_prompt = f"{system_prompt}\n\nStudent Question: {user_message}\n\nYour Response:"
        
        response = client.models.generate_content(
            model='gemini-3-flash-preview',  # Fast and has quota available
            contents=full_prompt
        )
        
        return {
            "response": response.text,
            "status": "success"
        }
    except Exception as e:
        return {
            "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
            "status": "error",
            "error": str(e)
        }

# Save student data
@app.post("/save-student")
async def save_student(student_data: StudentData, db: Session = Depends(get_db)):
    try:
        # Create new student record
        student = Student(
            name=student_data.name,
            academic_group=student_data.academic_group,
            gpa=student_data.gpa,
            interested_department=student_data.interested_department,
            preferred_university_type=student_data.preferred_university_type
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        
        return {
            "status": "success",
            "message": "Student data saved successfully",
            "student_id": student.id
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Get all students
@app.get("/students")
async def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return {
        "students": students,
        "total": len(students)
    }

# Get universities
@app.get("/universities")
async def get_universities():
    return {
        "universities": universities,
        "total": len(universities)
    }
