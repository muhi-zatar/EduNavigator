from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./universities.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database model
class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    name = Column(String, nullable=False)
    website = Column(String, nullable=False)

# Create the database
Base.metadata.create_all(bind=engine)

# Pydantic model for validation
class UniversityCreate(BaseModel):
    country: str
    name: str
    website: str

class UniversityResponse(UniversityCreate):
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

@app.post("/universities/", response_model=UniversityResponse)
def create_university(university: UniversityCreate, db: Session = Depends(get_db)):
    db_university = University(**university.dict())
    db.add(db_university)
    db.commit()
    db.refresh(db_university)
    return db_university

@app.get("/universities/", response_model=List[UniversityResponse])
def list_universities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    universities = db.query(University).offset(skip).limit(limit).all()
    return universities

@app.on_event("startup")
def populate_universities():
    db = SessionLocal()
    csv_file_path = 'files/world-universities.csv'
    try:
        data = pd.read_csv(csv_file_path, header=None)
        data.columns = ["country", "name", "website"]

        # Drop rows with missing values
        data = data.dropna(subset=["country", "name", "website"])

        for _, row in data.iterrows():
            if not db.query(University).filter_by(name=row['name']).first():
                db.add(University(country=row['country'], name=row['name'], website=row['website']))
        db.commit()
    except Exception as e:
        print(f"Error populating database: {e}")
    finally:
        db.close()

