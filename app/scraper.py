from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time

def get_top_internships(skills, education, location, top_n=4):
    skill_query = "-".join(skills).lower()
    url = f"https://internshala.com/internships/internship-in-{location.lower()}/keywords-{skill_query}"

    # Setup Selenium Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/chromium-browser"  # ensure Chromium path
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(3)  # wait for JS
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    cards = soup.find_all("div", class_="individual_internship")
    internships = []

    for card in cards:
        # Role
        role_tag = card.find("h3")
        role = role_tag.get_text(strip=True) if role_tag else "N/A"

        # Company
        company_tag = card.find("p")
        company = company_tag.get_text(strip=True) if company_tag else "N/A"

        # Location
        loc_tag = card.find("div", class_="row-1-item locations")
        loc = loc_tag.find("a").get_text(strip=True) if loc_tag else "N/A"

        # Stipend
        stipend_tag = card.find("span", class_="stipend")
        stipend = stipend_tag.get_text(strip=True) if stipend_tag else "N/A"

        # Duration
        duration = "N/A"
        duration_tag = card.find_all("div", class_="row-1-item")
        for d in duration_tag:
            if d.find("i", class_="ic-16-calendar"):
                duration = d.find("span").get_text(strip=True)
                break

        # Link
        link = "https://internshala.com" + card.get("data-href", "")

        # Full job description
        about_tag = card.find("div", class_="about_job")
        desc_tag = about_tag.find("div", class_="text") if about_tag else None
        description = desc_tag.get_text(" ", strip=True) if desc_tag else ""
        # Combine with role/company/location for TF-IDF
        text_for_tfidf = f"{role} {company} {loc} {description}"

        internships.append({
            "Role": role,
            "Company": company,
            "Location": loc,
            "Duration": duration,
            "Stipend": stipend,
            "Link": link,
            "Description": description
        })

    # TF-IDF Ranking
    corpus = [i["Description"] for i in internships]
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(corpus)

    query = " ".join(skills)
    query_vec = tfidf.transform([query])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Attach scores
    for i, score in enumerate(scores):
        internships[i]["Score"] = score

    df = pd.DataFrame(internships).sort_values(by="Score", ascending=False)
    # Show full link
    pd.set_option('display.max_colwidth', None)
    return df
