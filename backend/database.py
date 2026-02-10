from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create base class for database models
Base = declarative_base()

# Define Student model
class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    academic_group = Column(String, nullable=True)
    gpa = Column(Float, nullable=True)
    interested_department = Column(String, nullable=True)
    preferred_university_type = Column(String, nullable=True)

# Create database engine
engine = create_engine('sqlite:///students.db', connect_args={"check_same_thread": False})

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()