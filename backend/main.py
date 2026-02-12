import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from groq import Groq
import json
from database import get_db, Student

# Load environment variables
load_dotenv()

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
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

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


# Helper function to extract student info from message
def extract_student_info(message: str, db: Session):
    """Extract and save student information from user message"""
    student_data = {}
    
    # Extract GPA (e.g., "my gpa is 4.7", "GPA: 4.5", "I have 4.8")
    gpa_patterns = [
        r'(?:gpa|GPA|result|score)(?:\s+is|\s*:)?\s*(\d+\.?\d*)',
        r'(?:I have|got|scored)\s+(?:a\s+)?(\d+\.?\d*)\s*(?:gpa|GPA)',
        r'(\d+\.?\d*)\s+(?:gpa|GPA)'
    ]
    for pattern in gpa_patterns:
        gpa_match = re.search(pattern, message)
        if gpa_match:
            try:
                gpa_value = float(gpa_match.group(1))
                if 0 <= gpa_value <= 5.0:  # Valid GPA range
                    student_data['gpa'] = gpa_value
                    break
            except ValueError:
                continue
    
    # Extract academic group
    if re.search(r'\b(science|Science|SCIENCE)\b', message):
        student_data['academic_group'] = 'Science'
    elif re.search(r'\b(commerce|Commerce|COMMERCE|business|Business)\b', message):
        student_data['academic_group'] = 'Commerce'
    elif re.search(r'\b(arts|Arts|ARTS|humanities|Humanities)\b', message):
        student_data['academic_group'] = 'Arts'
    
    # Extract interested department
    departments = ['CSE', 'EEE', 'BBA', 'English', 'Economics', 'ME', 'CE', 'IPE',
                   'Architecture', 'Physics', 'Chemistry', 'Civil Engineering', 
                   'Mechanical Engineering', 'Electrical Engineering']
    for dept in departments:
        if re.search(rf'\b{dept}\b', message, re.IGNORECASE):
            student_data['interested_department'] = dept.upper() if len(dept) <= 3 else dept
            break
    
    # Extract university preference
    if re.search(r'\b(public|Public|PUBLIC|govt|government)\b', message):
        student_data['preferred_university_type'] = 'Public'
    elif re.search(r'\b(private|Private|PRIVATE)\b', message):
        student_data['preferred_university_type'] = 'Private'
    
    # Extract name (if they say "my name is..." or "I'm..." or "I am...")
    name_patterns = [
        r'(?:my name is|I am|I\'m|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:this is|speaking is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    ]
    for pattern in name_patterns:
        name_match = re.search(pattern, message, re.IGNORECASE)
        if name_match:
            student_data['name'] = name_match.group(1).title()
            break
    
    # If we found any info, save it to database
    if student_data:
        try:
            student = Student(**student_data)
            db.add(student)
            db.commit()
            db.refresh(student)
            print(f"✅ Saved student data: {student_data}")
            return student.id, student_data
        except Exception as e:
            print(f"❌ Error saving student data: {e}")
            db.rollback()
            return None, student_data
    
    return None, {}


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "University Admission Assistant API",
        "status": "running",
        "total_universities": len(universities),
        "endpoints": {
            "chat": "/chat",
            "students": "/students",
            "universities": "/universities",
            "save_student": "/save-student"
        }
    }


# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    user_message = request.message
    
    # Extract and save student information from the message
    student_id, extracted_info = extract_student_info(user_message, db)
    
    # Get student data if student_id is provided or just extracted
    student_context = ""
    if request.student_id:
        student = db.query(Student).filter(Student.id == request.student_id).first()
        if student:
            student_context = f"""
Student Profile (from database):
- Name: {student.name or 'Not provided'}
- Academic Group: {student.academic_group or 'Not provided'}
- GPA: {student.gpa or 'Not provided'}
- Interested Department: {student.interested_department or 'Not provided'}
- Preferred University Type: {student.preferred_university_type or 'Not provided'}
"""
    elif extracted_info:
        # Use the newly extracted info
        info_lines = []
        if 'name' in extracted_info:
            info_lines.append(f"- Name: {extracted_info['name']}")
        if 'gpa' in extracted_info:
            info_lines.append(f"- GPA: {extracted_info['gpa']}")
        if 'academic_group' in extracted_info:
            info_lines.append(f"- Academic Group: {extracted_info['academic_group']}")
        if 'interested_department' in extracted_info:
            info_lines.append(f"- Interested Department: {extracted_info['interested_department']}")
        if 'preferred_university_type' in extracted_info:
            info_lines.append(f"- Preferred University Type: {extracted_info['preferred_university_type']}")
        
        if info_lines:
            student_context = f"""
Student Information (just provided):
{chr(10).join(info_lines)}

Note: I have saved this information for future reference.
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
4. If you don't have complete information (GPA, academic group, or department preference), politely ask for the missing details
5. Be friendly, encouraging, and helpful
6. Provide specific recommendations with clear reasons
7. When students provide their information, acknowledge it briefly and use it for personalized recommendations
8. Format your responses clearly with proper line breaks and structure

Important Guidelines:
- Only recommend universities where admission_status is "Open"
- Only recommend universities where the student's GPA meets or exceeds the minimum_gpa requirement
- If a student asks about a specific department, show ALL universities offering that department (both public and private)
- If a student specifies public/private preference, filter accordingly
- Group recommendations by university type (Public/Private)
- Always mention the minimum GPA requirement for each university

Response Format Guidelines:
- Use clear sections for Public and Private universities
- List each university with its key details (name, minimum GPA, location if relevant)
- Keep responses concise but informative
- Use natural, conversational language

Answer the student's question based on the available university data."""

    try:
        # Generate response using Gemini API
        full_prompt = f"{system_prompt}\n\nStudent Question: {user_message}\n\nYour Response:"
        
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=full_prompt
        )
        
        return {
            "response": response.text,
            "status": "success",
            "student_id": student_id,  # Return student_id so frontend can track it
            "extracted_info": extracted_info if extracted_info else None
        }
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        # Print detailed error to logs
        print("=" * 50)
        print("ERROR IN CHAT ENDPOINT:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Full traceback:")
        print(error_details)
        print("=" * 50)
        
        # Check for specific errors and provide user-friendly messages
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "resource has been exhausted" in error_str:
            user_message = "⚠️ API quota exceeded. The free tier limit has been reached. Please try again in a few minutes or contact the administrator."
        elif "404" in error_str or "not found" in error_str:
            user_message = "⚠️ AI model not found. The model may have been updated. Please contact support."
        elif "401" in error_str or "403" in error_str or "invalid" in error_str:
            user_message = "⚠️ API key is invalid or expired. Please contact the administrator."
        else:
            user_message = f"⚠️ I encountered a technical error. Please try again. Error: {str(e)[:100]}"
        
        return {
            "response": user_message,
            "status": "error",
            "error": str(e)
        }


# Save student data manually
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
            "student_id": student.id,
            "student_data": {
                "name": student.name,
                "academic_group": student.academic_group,
                "gpa": student.gpa,
                "interested_department": student.interested_department,
                "preferred_university_type": student.preferred_university_type
            }
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Failed to save student data: {str(e)}"
        }


# Get all students
@app.get("/students")
async def get_students(db: Session = Depends(get_db)):
    try:
        students = db.query(Student).all()
        student_list = []
        
        for student in students:
            student_list.append({
                "id": student.id,
                "name": student.name,
                "academic_group": student.academic_group,
                "gpa": student.gpa,
                "interested_department": student.interested_department,
                "preferred_university_type": student.preferred_university_type
            })
        
        return {
            "status": "success",
            "total_students": len(student_list),
            "students": student_list
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch students: {str(e)}"
        }


# Get universities
@app.get("/universities")
async def get_universities():
    return {
        "status": "success",
        "total": len(universities),
        "universities": universities
    }


# Get a specific student by ID
@app.get("/students/{student_id}")
async def get_student(student_id: int, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        
        if not student:
            return {
                "status": "error",
                "message": f"Student with ID {student_id} not found"
            }
        
        return {
            "status": "success",
            "student": {
                "id": student.id,
                "name": student.name,
                "academic_group": student.academic_group,
                "gpa": student.gpa,
                "interested_department": student.interested_department,
                "preferred_university_type": student.preferred_university_type
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch student: {str(e)}"
        }