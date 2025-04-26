import nltk
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from collections import Counter
from sklearn.metrics import silhouette_score
import pdfplumber
import os
from fpdf import FPDF
import uuid
from fastapi import HTTPException, UploadFile, Request, File
from interview_analysis.engagement import extract_questions, extract_text_from_pdf
from core_files1.describe import explain_diversity_metric

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)


def analyze_question_diversity(questions, n_clusters=5):
    if len(questions) == 0:
        raise HTTPException(status_code=400, detail="No questions found in the document.")

    n_clusters = max(2, min(len(questions) -1, n_clusters))

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(questions)

    embeddings = np.array(embeddings)

    kmeans = KMeans(n_clusters=n_clusters, random_state=3, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    cluster_counts = Counter(labels)

    cluster_counts = {int(k): int(v) for k, v in cluster_counts.items()}
    
    if len(set(labels)) > 1 and len(questions) > n_clusters:
        diversity_score = silhouette_score(embeddings, labels, metric='euclidean')
        diversity_score = float(diversity_score)
    else:
        diversity_score = 0.0

    return {
        "diversity_score": round(diversity_score, 3) *100,
        "cluster_counts": cluster_counts
    }

def generate_diversity_report(json_response):
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_diversity.pdf"
    report_path = os.path.join(REPORTS_DIR, report_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Interview Question Diversity Analysis Report", ln=True, align="C")
    pdf.ln(10)

    report_content = json_response.get("report", "").split("\n\n")

    for section in report_content:
        section = section.replace("**", "").replace("*", "").replace("###", "").strip()

        if section.startswith("Definition") or section.startswith("Interpretation") or section.startswith("Contextual Insights"):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, section, ln=True, align="L")
            pdf.ln(3)
        elif ":" in section:
            section_title, section_value = section.split(":", 1)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, section_title.strip(), ln=True, align="L")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, section_value.strip(), ln=True, align="L")
            pdf.ln(5)
        elif "|" in section:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Cluster Distribution & Question Analysis", ln=True, align="L")
            pdf.ln(3)
            table_rows = section.split("\n")
            for row in table_rows:
                if "|" in row:
                    columns = row.split("|")[1:-1]
                    pdf.cell(60, 8, columns[0].strip(), border=1, align="C")
                    pdf.cell(60, 8, columns[1].strip(), border=1, align="C")
                    pdf.ln()
            pdf.ln(5)
        else:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 7, section, align="L")
            pdf.ln(3)

    pdf.output(report_path)
    return report_path

async def diversity_analysis(request: Request, file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/plain", "application/pdf"]:
            raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")
        
        if file.content_type == "text/plain":
            text = (await file.read()).decode("utf-8")

        elif file.content_type == "application/pdf":
            text = extract_text_from_pdf(file.file)

        questions = extract_questions(text)
        metric = analyze_question_diversity(questions)
        report_content = explain_diversity_metric(metric)
        report_name = generate_diversity_report(report_content)
        pdf_path = f"{request.base_url}{report_name}"

        return {
            "Message": "Interview question diversity check completed successfully",
            "Question_diversity_report": pdf_path
        }

    except Exception as e:
        return {"error": str(e)}
