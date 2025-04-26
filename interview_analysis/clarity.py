from fastapi import HTTPException, UploadFile, File, Request
import textstat
import spacy
import language_tool_python
from nltk.tokenize import sent_tokenize, word_tokenize
import pdfplumber
import re
import uuid
from fpdf import FPDF
from core_files1.describe import explain_clarity
import os

nlp = spacy.load("en_core_web_sm")
tool = language_tool_python.LanguageTool('en-US')

def analyze_question_clarity(question: str):
    try:
        analysis = {}

        word_count = len(word_tokenize(question))
        analysis["Word Count"] = word_count
        analysis["Conciseness"] = (
            "Too short, may lack clarity." if word_count < 5 else
            "Too long, may be confusing." if word_count > 20 else
            "Good length."
        )

        readability_score = textstat.flesch_reading_ease(question)
        analysis["Readability Score"] = readability_score
        analysis["Readability"] = (
            "Difficult to understand." if readability_score < 50 else
            "Easy to understand." if readability_score > 70 else
            "Moderately clear."
        )

        grammar_errors = tool.check(question)
        analysis["Grammar Issues"] = len(grammar_errors)
        analysis["Grammar Clarity"] = "Good" if len(grammar_errors) == 0 else "Needs improvement."

        doc = nlp(question)
        complex_structure = any(token.dep_ in ["advcl", "ccomp", "xcomp"] for token in doc)
        analysis["Syntactic Complexity"] = "Complex" if complex_structure else "Simple"

        vague_words = ["this", "that", "it", "something", "somewhat", "kind of", "sort of"]
        found_vague = [word for word in vague_words if word in question.lower()]
        analysis["Vagueness Detected"] = ", ".join(set(found_vague)) if found_vague else "None"
    
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing question clarity: {str(e)}")

def analyze_transcript_clarity(transcript: str):
    try:
        analysis = {}

        sentences = sent_tokenize(transcript)
        total_sentences = len(sentences)
        total_words = sum(len(word_tokenize(sentence)) for sentence in sentences)

        questions = [sentence.strip() for sentence in sentences if sentence.strip().endswith("?")]
        total_questions = len(questions)

        readability_scores = [textstat.flesch_reading_ease(sentence) for sentence in sentences if sentence.strip()]
        avg_readability = sum(readability_scores) / len(readability_scores) if readability_scores else 0
        avg_readability = round(avg_readability, 2)

        total_grammar_issues = sum(len(tool.check(sentence)) for sentence in sentences)

        complex_sentences = sum(
            any(token.dep_ in ["advcl", "ccomp", "xcomp"] for token in nlp(sentence)) for sentence in sentences
        )

        vague_words = ["this", "that", "it", "something", "somewhat", "kind of", "sort of"]
        found_vague = [word for word in vague_words if word in transcript.lower()]


        question_analyses = {f"Question {i+1}": analyze_question_clarity(question) for i, question in enumerate(questions)}

        analysis["Total Sentences"] = total_sentences
        analysis["Total Words"] = total_words
        analysis["Total Questions"] = total_questions
        analysis["Average Readability Score"] = avg_readability
        analysis["Readability"] = (
            "Difficult to understand" if avg_readability < 50 else
            "Easy to understand" if avg_readability > 70 else
            "Moderately clear"
        )
        analysis["Total Grammar Issues"] = total_grammar_issues
        analysis["Grammar Clarity"] = "Good" if total_grammar_issues == 0 else "Needs improvement"
        analysis["Complex Sentences"] = complex_sentences
        analysis["Syntactic Complexity"] = "Complex" if complex_sentences > total_sentences * 0.3 else "Simple"
        analysis["Vagueness Detected"] = ", ".join(set(found_vague)) if found_vague else "None"
        analysis["Question Analysis"] = question_analyses

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing transcript clarity: {str(e)}")

def extract_text_from_pdf(file) -> str:
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text from PDF: {str(e)}")


def generate_clarity_report(report_content: str):
    unique_id = str(uuid.uuid4())
    report_filename = f"{unique_id}_clarity_report.pdf"
    report_path = os.path.join("reports", report_filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()

    pdf.set_font("Arial", "", 12)

    for line in report_content.split("\n"):
        pdf.multi_cell(0, 8, line)
        pdf.ln(2)

    pdf.output(report_path)
    return report_path

async def analyze_transcript(request: Request, file: UploadFile = File(...)):
    try:
        if file.content_type not in ["text/plain", "application/pdf"]:
            raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")

        if file.content_type == "text/plain":
            text = (await file.read()).decode("utf-8")
        elif file.content_type == "application/pdf":
            text = extract_text_from_pdf(file.file)

        result = analyze_transcript_clarity(text)
        report_content = explain_clarity(result)
        report_content = remove_emojis(report_content)
        report_content = remove_special_symbols(report_content)
        report_content = replace_unicode(report_content)
        report_content = remove_special_symbols(report_content)
        report_name = generate_clarity_report(report_content)

        pdf_path = f"{request.base_url}{report_name}"

        return {
            "Message": "Conversation analysis report is generated successfully",
            "pdf_path": pdf_path
        }
    
    except Exception as e:
        return {"error": str(e)}

def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"  
                               u"\U0001F680-\U0001F6FF"  
                               u"\U0001F700-\U0001F77F"  
                               u"\U0001F780-\U0001F7FF" 
                               u"\U0001F800-\U0001F8FF"  
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def remove_special_symbols(text):
    text = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^-{3,}", "", text)
    return text.strip()

def replace_unicode(text):
    replacements = {
        "•": "-",
        "✔": "[OK]",
        "❌": "[X]",
        "➡": "->",
        "“": '"', "”": '"', 
        "‘": "'", "’": "'",
    }
    for unicode_char, ascii_equiv in replacements.items():
        text = text.replace(unicode_char, ascii_equiv)
    return text

def remove_special_symbols(text):
    text = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", text)  
    
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  

    text = re.sub(r"^\s*[-*]\s*", "", text, flags=re.MULTILINE)

    text = re.sub(r"[*_]+$", "", text)  
    text = text.strip()

    return text
