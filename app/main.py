# app/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.scraper import get_top_internships

app = FastAPI()

class UserInput(BaseModel):
    skills: List[str]
    education: str
    location: str

@app.post("/recommend_internships")
def recommend(input_data: UserInput):
    df = get_top_internships(
        skills=input_data.skills,
        education=input_data.education,
        location=input_data.location,
        top_n=4
    )
    return df.to_dict(orient="records")
