from fastapi import FastAPI
from pydantic import BaseModel
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

class AcceptanceInput(BaseModel):
    gpa: float
    test_scores: float
    extracurricular: str

@app.post("/calculate-acceptance/")
def calculate_acceptance(input_data: AcceptanceInput):
    # Mock calculation logic
    probability = min((input_data.gpa * 0.5 + input_data.test_scores * 0.3), 100)
    return {"acceptance_probability": f"{probability:.2f}%"}
