from fuzzywuzzy import fuzz
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from core_files.metrics import friendly_keywords, authoritative_keywords, neutral_keywords
import pdfplumber
import os
from fpdf import FPDF
import uuid
from fastapi import HTTPException, Request, File, UploadFile
from core_files1.describe import explain_tone
from interview_analysis.engagement import extract_text_from_pdf, extract_questions

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

sia = SentimentIntensityAnalyzer()

def detect_tone(text, threshold=80):
    sentences = [s.strip() for s in text.split("\n") if s.strip()]

    neutral_count = 0
    friendly_count = 0
    authoritative_count = 0
    total_sentences = len(sentences)

    for sentence in sentences:
        sentiment_score = sia.polarity_scores(sentence)["compound"]

        if any(fuzz.partial_ratio(word.lower(), sentence.lower()) > threshold for word in friendly_keywords) or sentiment_score > 0.3:
            friendly_count += 1
            continue

        elif any(fuzz.partial_ratio(word.lower(), sentence.lower()) > threshold for word in authoritative_keywords):
            authoritative_count += 1
            continue

        elif any(fuzz.partial_ratio(word.lower(), sentence.lower()) > threshold for word in neutral_keywords) or (-0.3 <= sentiment_score <= 0.3):
            neutral_count += 1

    neutral_tone_percentage = (neutral_count / total_sentences) * 100 if total_sentences > 0 else 0
    friendly_tone_percentage = (friendly_count / total_sentences) * 100 if total_sentences > 0 else 0
    authoritative_tone_percentage = (authoritative_count / total_sentences) * 100 if total_sentences > 0 else 0

    return{
        "Neutral_tone_percentage": round(neutral_tone_percentage, 3),
        "Friendly_tone_percentage": round(friendly_tone_percentage, 3),
        "Authoritative_tone_percentage": round(authoritative_tone_percentage, 3)
    }

def generate_tone_analysis_pdf(report_text):
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_tone_analysis.pdf"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Interview Tone Analysis Report", ln=True, align="C")
    pdf.ln(10)

    report_lines = report_text.split("\n")

    for line in report_lines:
        line = line.strip().replace("**", "")

        if line.startswith("###"):
            pdf.set_font("Arial", "B", 14)
            pdf.multi_cell(0, 8, line.replace("###", "").strip(), align="L")
            pdf.ln(3)
        elif line.endswith(":"):
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, line.strip(), align="L")
            pdf.ln(2)
        elif line.startswith("- "):
            pdf.set_font("Arial", "", 12)
            pdf.cell(5)
            pdf.multi_cell(0, 7, line.strip(), align="L")
        elif line:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 7, line, align="L")
            pdf.ln(2)

    pdf.output(report_path)
    return report_path

async def measure_tone(request: Request, file: UploadFile = File(...)):
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
        
        result = detect_tone(text)
        neutral_tone = result["Neutral_tone_percentage"]
        friendly_tone = result["Friendly_tone_percentage"]
        authoritative_tone = result["Authoritative_tone_percentage"]

        tone_analysis_content = explain_tone(neutral_tone, friendly_tone, authoritative_tone)
        report_name = generate_tone_analysis_pdf(tone_analysis_content)

        pdf_path = f"{request.base_url}{report_name}"

        return {
            "Message": "Interviewer's tone analysis report is generated",
            "Report_path":pdf_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
