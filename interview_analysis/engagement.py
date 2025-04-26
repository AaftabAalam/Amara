from rapidfuzz import fuzz
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import pdfplumber
import re
from fpdf import FPDF
from typing import List
import os
import uuid
from core_files.metrics import open_ended_keywords, follow_up_phrases, active_listening_phrases
from core_files1.describe import explain_engagement_metric

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def detect_open_ended_questions(text, keywords, threshold=80):
    sentences = text.split("\n")
    total_sentences = len([s for s in sentences if s.strip()])
    open_ended_count = 0

    for sentence in sentences:
        if sentence.strip():
            for keyword in keywords:
                if fuzz.partial_ratio(keyword.lower(), sentence.lower()) > threshold:
                    open_ended_count += 1
                    break

    percentage = (open_ended_count / total_sentences) * 100 if total_sentences > 0 else 0
    return percentage

def detect_follow_up(text, keywords, threshold=80):
    sentences = text.split("\n")
    total_sentences = len([s for s in sentences if s.strip()])
    follow_up_count = 0

    for sentence in sentences:
        if sentence.strip():
            for keyword in keywords:
                if fuzz.partial_ratio(keyword.lower(), sentence.lower()) > threshold:
                    follow_up_count += 1
                    break
    
    percentage = (follow_up_count / total_sentences) * 100 if total_sentences > 0 else 0
    return percentage

def detect_active_listening(text, phrases, threshold=80):
    sentences = [s.strip() for s in text.split("\n") if s.strip()]
    total_sentences = len(sentences)
    matched_sentences = set()

    for sentence in sentences:
        for phrase in phrases:
            if fuzz.partial_ratio(phrase.lower(), sentence.lower()) > threshold:
                matched_sentences.add(sentence)
                break

    percentage = (len(matched_sentences) / total_sentences) * 100 if total_sentences > 0 else 0
    return percentage

def calculate_total_engagement(text, open_ended_keywords, follow_up_phrases, active_listening_phrases):
    open_ended = detect_open_ended_questions(text, open_ended_keywords)
    follow_up = detect_follow_up(text, follow_up_phrases)
    active_listening = detect_active_listening(text, active_listening_phrases)

    total_engagement = active_listening + follow_up + open_ended
    normalized_engagement = min(total_engagement, 100)

    return{
        "Active_listening_engagement": round(active_listening, 2),
        "Follow_up_engagement": round(follow_up, 2),
        "Open_ended_engagement": round(open_ended, 2),
        "Total_engagement": round(normalized_engagement, 2)
    }

def extract_questions(text: str) -> List[str]:
    try:
        if not isinstance(text, str):
            raise ValueError("Input text must be a string")
        
        question_pattern = r'([A-Z][^\.!?]*\?)'
        questions = re.findall(question_pattern, text)
        return questions if questions else []
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting questions from text: {str(e)}")

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(file) -> str:
    try:
        with pdfplumber.open(file) as pdf:
            text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return clean_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

def generate_engagement_report(json_response):
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_engagement.pdf"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Engagement Metrics Analysis Report", ln=True, align="C")
    pdf.ln(10)

    for metric, content in json_response.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, metric.replace("_", " "), ln=True, align="L")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, content.replace("### ", "").replace("**", ""), align="L")
        pdf.ln(5)
    pdf.output(report_path)

    return report_path

async def engagement_analysis(request: Request, file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/plain", "application/pdf"]:
            raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")
        
        if file.content_type == "text/plain":
            text = (await file.read()).decode("utf-8")

        elif file.content_type == "application/pdf":
            text = extract_text_from_pdf(file.file)
        
        questions = extract_questions(text) or []
        result = calculate_total_engagement("\n".join(questions), open_ended_keywords, follow_up_phrases, active_listening_phrases)

        report = {}
        for metric, value in result.items():
            report[metric] = explain_engagement_metric({metric: value}).get(metric, "Error Processing Metric Key")

        report_name = generate_engagement_report(report)
        pdf_path = f"{request.base_url}{report_name}"

        return {
            "message": "Engagement analysis completed successfully",
            "Engagement_pdf_path": pdf_path
        }
    
    except Exception as e:
        return {"error": str(e)}
