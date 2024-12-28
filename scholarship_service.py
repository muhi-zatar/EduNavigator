from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# FastAPI app initialization
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for all origins (during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Database setup
DATABASE_URL = "sqlite:///./scholarships.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database model
class Scholarship(Base):
    __tablename__ = "scholarships"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    eligibility_criteria = Column(Text, nullable=False)
    funding_details = Column(Text, nullable=False)
    application_deadline = Column(Date, nullable=False)
    study_level = Column(String, nullable=False)
    country = Column(String, nullable=False)
    university_association = Column(String, nullable=True)
    application_link = Column(String, nullable=False)

# Create the database
Base.metadata.create_all(bind=engine)

# Pydantic model for validation
class ScholarshipCreate(BaseModel):
    name: str
    eligibility_criteria: str
    funding_details: str
    application_deadline: str  # Use ISO format: YYYY-MM-DD
    study_level: str
    country: str
    university_association: Optional[str] = None
    application_link: str

class ScholarshipResponse(ScholarshipCreate):
    id: int

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints

@app.post("/scholarships/", response_model=ScholarshipResponse)
def create_scholarship(scholarship: ScholarshipCreate, db: Session = Depends(get_db)):
    db_scholarship = Scholarship(**scholarship.dict())
    db.add(db_scholarship)
    db.commit()
    db.refresh(db_scholarship)
    return db_scholarship

@app.get("/scholarships/", response_model=List[ScholarshipResponse])
def list_scholarships(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    scholarships = db.query(Scholarship).offset(skip).limit(limit).all()
    return scholarships

@app.get("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    scholarship = db.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship

# Synthesis data (populate database for testing)
@app.on_event("startup")
def populate_synthesis_data():
    db = SessionLocal()
    if not db.query(Scholarship).first():
        sample_scholarships = [
            Scholarship(
                name="Middle East STEM Scholarship",
                eligibility_criteria="Minimum GPA of 3.0, residents of Middle East",
                funding_details="Full tuition, travel expenses covered",
                application_deadline="2024-12-31",
                study_level="Undergraduate",
                country="United Arab Emirates",
                university_association="University of Dubai",
                application_link="https://example.com/apply"
            ),
            Scholarship(
                name="Women in Tech Fellowship",
                eligibility_criteria="Female students pursuing a Master's in Computer Science",
                funding_details="$10,000 yearly stipend",
                application_deadline="2024-11-15",
                study_level="Graduate",
                country="Jordan",
                university_association="",
                application_link="https://example.com/wit"
            ),
        ]
        db.bulk_save_objects(sample_scholarships)
        db.commit()
    db.close()
