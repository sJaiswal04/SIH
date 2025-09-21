from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import time

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    skills: str
    education: str
    location: str
    top_n: int = 5

def scrape_internships(skills, location, top_n):
    skill_list = [skill.strip() for skill in skills.split(",")]
    skill_query = "-".join(skill_list).lower()
    url = f"https://internshala.com/internships/internship-in-{location.lower()}/keywords-{skill_query}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    cards = soup.find_all("div", class_="individual_internship")
    internships = []

    for card in cards:
        role = card.find("h3").get_text(strip=True) if card.find("h3") else "N/A"
        company = card.find("p").get_text(strip=True) if card.find("p") else "N/A"
        loc_tag = card.find("div", class_="row-1-item locations")
        loc = loc_tag.get_text(strip=True) if loc_tag else "N/A"
        stipend_tag = card.find("span", class_="stipend")
        stipend = stipend_tag.get_text(strip=True) if stipend_tag else "N/A"
        duration = "N/A"
        for d in card.find_all("div", class_="row-1-item"):
            if d.find("i", class_="ic-16-calendar"):
                duration = d.get_text(strip=True)
                break
        link = "https://internshala.com" + card.get("data-href", "#")
        desc_tag = card.find("div", class_="about_job")
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""

        internships.append({
            "role": role,
            "company": company,
            "location": loc,
            "duration": duration,
            "stipend": stipend,
            "link": link,
            "description": description
        })

    # Ranking with TF-IDF
    if internships:
        corpus = [i["description"] for i in internships]
        tfidf = TfidfVectorizer(stop_words="english", max_features=5000)
        tfidf_matrix = tfidf.fit_transform(corpus)

        query = " ".join(skill_list)
        query_vec = tfidf.transform([query])
        scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

        for i, score in enumerate(scores):
            internships[i]["score"] = round(score * 100, 1)

        df = pd.DataFrame(internships).sort_values(by="score", ascending=False)
        return df.head(top_n).to_dict(orient="records")
    return []

@app.post("/search")
def search_internships(request: SearchRequest):
    results = scrape_internships(request.skills, request.location, request.top_n)
    return {"results": results}
