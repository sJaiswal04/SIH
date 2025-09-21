# Resume Skill Extractor

Extract skills from resumes using Python and Gradio.

---

## **Live Demo**

Test the app directly in your browser (no setup needed):  

[Open Resume Skill Extractor on Hugging Face Spaces](https://huggingface.co/spaces/RSLTFRMR/resume_checker)

---

## **How it works**

1. Upload a resume (PDF, DOCX, or TXT).  
2. Upload a `skills.txt` file containing your skill list.  
3. The app extracts all matching skills and displays them.

---

## **Files in this repo**

- `app.py` → Gradio interface and skill extraction logic.  
- `requirements.txt` → Python dependencies.  
- `skills.txt` → List of skills to match in resumes.  

---

## **Notes**

- The SpaCy model `en_core_web_lg` is automatically downloaded when the app runs on Hugging Face Spaces.  
- Works instantly through the live demo link; no Python installation required.
