import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from collections import Counter
from core_files.metrics1 import age_keywords, race_keywords, gender_keywords
import re
import os
import uuid
from fastapi import Request, UploadFile, File, HTTPException
from fpdf import FPDF
from interview_analysis.engagement import extract_questions, extract_text_from_pdf
from core_files1.describe import explain_bias

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

sia = SentimentIntensityAnalyzer()
nlp = spacy.load("en_core_web_sm")

model = SentenceTransformer("all-MiniLM-L6-v2")

def detect_bias(questions_by_interviewer):
    interviewee_analysis = {}
    overall_questions = []
    all_sentiments = []

    for interviewee, questions in questions_by_interviewer.items():
        question_count = len(questions)
        embeddings = model.encode(questions)
        sentiments = [sia.polarity_scores(q)["compound"] for q in questions]

        gender_bias_count = 0
        race_bias_count = 0
        age_bias_count = 0

        for question in questions:
            doc = nlp(question)
            tokens = [token.text.lower() for token in doc]

            if any(word in tokens for word in gender_keywords):
                gender_bias_count += 1
            if any(word in tokens for word in race_keywords):
                race_bias_count += 1
            if any(word in tokens for word in age_keywords):
                age_bias_count += 1

        n_clusters = min(5, question_count)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        cluster_counts = Counter(labels)

        interviewee_analysis[interviewee] = {
            "total_questions": question_count,
            "avg_sentiment": round(sum(sentiments) / len(sentiments), 3) if sentiments else 0,
            "gender_bias_count": gender_bias_count,
            "race_bias_count": race_bias_count,
            "age_bias_count": age_bias_count,
            "topic_diversity": len(cluster_counts),
        }
        
        overall_questions.extend(questions)
        all_sentiments.extend(sentiments)

    return interviewee_analysis

def clean_text(text):
    cleaned_text = re.sub(r"[*#]+", "", text).strip()
    return cleaned_text

def get_bias_report(bias_explanation: str) -> str:
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_bias_analysis.pdf"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Interview Bias Analysis Report", ln=True, align="C")
    pdf.ln(10)

    lines = bias_explanation.split("\n")
    for line in lines:
        cleaned_line = clean_text(line)

        if cleaned_line.strip() == "":
            pdf.ln(5)
            continue

        if cleaned_line.startswith("1.") or cleaned_line.startswith("2.") or cleaned_line.startswith("3.") or cleaned_line.startswith("4."):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, cleaned_line, ln=True, align="L")
            pdf.ln(5)

        elif cleaned_line.endswith(":"):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, cleaned_line, ln=True, align="L")

        else:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 7, cleaned_line, align="L")

    pdf.output(report_path, "F")
    return report_path

async def analyze_bias(request: Request, file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/plain", "application/pdf"]:
                raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

        if file.content_type == "text/plain":
            text = (await file.read()).decode("utf-8")
        elif file.content_type == "application/pdf":
            text = extract_text_from_pdf(file.file)
        
        questions_by_interviewer = extract_questions(text) or []

        if not questions_by_interviewer:
            return {"message": "No questions found in the transcript."}

        transformed_data = {
            "Candidate_A": questions_by_interviewer
        }

        bias_result = detect_bias(transformed_data)
        bias_explanation = explain_bias(bias_result)
        report_name = get_bias_report(bias_explanation)

        pdf_path = f"{request.base_url}{report_name}"

        return {
            "Message": "Bias analysis report is generated successfully.",
            "Pdf_path": pdf_path
        }
    except Exception as e:
        return {"error": str(e)}
