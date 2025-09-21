import re
import pdfplumber
from docx import Document
import spacy
import gradio as gr

# Load SpaCy model once
nlp = spacy.load("en_core_web_lg")

# ----------------------------
# Extract text from resume
# ----------------------------
def extract_text(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file.name) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    elif name.endswith(".docx"):
        doc = Document(file.name)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type. Use PDF or DOCX.")

# ----------------------------
# Load skills list (supports NamedString and file path)
# ----------------------------
def load_skills(skill_file):
    skills = []
    try:
        # Try reading as a normal file
        with open(skill_file.name, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except AttributeError:
        # If NamedString, decode directly
        lines = skill_file.read().decode("utf-8").splitlines()

    for line in lines:
        line = line.strip()
        if line:
            parts = [s.strip() for s in re.split(r',|\|', line) if s.strip()]
            skills.extend(parts)
    return skills

# ----------------------------
# Extract skills from resume text
# ----------------------------
def extract_skills(cv_text, skills_list):
    text_clean = re.sub(r'[\|\n,:\-]+', ' ', cv_text)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip().lower()
    found_skills = []
    for skill in skills_list:
        if skill.lower() in text_clean:
            found_skills.append(skill)
    return sorted(set(found_skills))

# ----------------------------
# Gradio interface function
# ----------------------------
def match_skills(resume_file, skills_file):
    try:
        cv_text = extract_text(resume_file)
        skills_list = load_skills(skills_file)
        matched = extract_skills(cv_text, skills_list)
        return "\n".join(matched) if matched else "No skills found."
    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------------
# Build Gradio UI
# ----------------------------
with gr.Blocks() as demo:
    gr.Markdown("## 📄 Resume Skill Extractor")
    gr.Markdown("Upload a resume (PDF/DOCX) and a skills list (.txt) to extract matching skills.")
    
    with gr.Row():
        resume_input = gr.File(label="Upload Resume (PDF/DOCX)")
        skills_input = gr.File(label="Upload Skills List (.txt)")
    output = gr.Textbox(label="Matched Skills", lines=15)
    
    submit_btn = gr.Button("Extract Skills")
    submit_btn.click(fn=match_skills, inputs=[resume_input, skills_input], outputs=output)

demo.launch()
