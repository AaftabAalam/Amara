from fastapi import HTTPException, Request, File, UploadFile
import joblib
import pdfplumber
import re
from typing import List, Dict
import os
import uuid
from fpdf import FPDF
from interview_analysis.engagement import extract_text_from_pdf
from core_files1.describe import classified_question_explanation


loaded_model = joblib.load("question_classifier.pkl")

def extract_questions(text: str) -> List[str]:
    try:
        if not isinstance(text, str):
            raise ValueError("Input text must be a string")
        
        question_pattern = r'([A-Z][^\.!?]*\?)'
        questions = re.findall(question_pattern, text)

        return questions if questions else []
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting questions from text: {str(e)}")
    
async def classify_questions(request: Request, file: UploadFile = File(...)) -> Dict[str, List[Dict[str, str]]]:
    try:
        if file.content_type not in ["text/plain", "application/pdf"]:
            raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

        if file.content_type == "text/plain":
            try:
                text = (await file.read()).decode("utf-8")
            except UnicodeDecodeError as ude:
                raise HTTPException(status_code=400, detail=f"Error decoding text file: {str(ude)}")
        elif file.content_type == "application/pdf":
            try:
                text = extract_text_from_pdf(file.file)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")

        try:
            questions = extract_questions(text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting questions from text: {str(e)}")

        if not questions:
            return {"message": "No questions found in the transcript."}

        predictions = loaded_model.predict(questions)
        result = [{"question": q, "category": c} for q, c in zip(questions, predictions)]

        question_category_explanation = classified_question_explanation(result)
        report_name = classified_questions_report(question_category_explanation)

        pdf_path = f"{request.base_url}{report_name}"

        return {
            "Message":"Interview questions classification report generated successfully.",
            "pdf_path": pdf_path
        }

    except Exception as e:
        return {"error": str(e)}


def classified_questions_report(json_response):
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_questions_report.pdf"
    report_path = os.path.join("reports", report_filename)
    
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Classified Questions Report", ln=True, align="C")
    pdf.ln(10)
    
    for item in json_response.get("questions", []):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Question:", ln=True, align="L")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, item["question"], align="L")
        pdf.ln(2)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Category:", ln=True, align="L")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, item["category"], ln=True, align="L")
        pdf.ln(2)
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Explanation:", ln=True, align="L")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, item["explanation"], align="L")
        pdf.ln(8)
    
    pdf.output(report_path)
    return report_path
