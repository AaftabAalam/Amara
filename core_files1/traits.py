from fastapi import Request, HTTPException
import os
import json
import uuid
import aiofiles
from fpdf import FPDF
from rapidfuzz import process, fuzz
from core_files1.categories import keyword_categories
from core_files1.describe import evaluate
from collections import Counter
from tenacity import retry, stop_after_attempt, wait_fixed


UPLOADS_DIR = "uploads"
REPORTS_DIR = "reports"

os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    replacements = {
        "\u2019": "'",
        "\u201C": '"',
        "\u201D": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text

@retry(stop=stop_after_attempt(5), wait=wait_fixed(2))
async def ensure_facet_availability(trait_percentages):
    explanation = evaluate(trait_percentages)
    if all(trait_data[3] for trait_data in explanation):
        return explanation
    raise ValueError("Facets not available, retrying...")

async def calculate_personality_trait(request: Request):
    try:
        data = await request.json()
        unique_id = str(uuid.uuid4())
        uploaded_path = os.path.join(UPLOADS_DIR, f"{unique_id}.json")

        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Invalid JSON format.")

        async with aiofiles.open(uploaded_path, "w", encoding="utf-8") as out_file:
            await out_file.write(json.dumps(data, indent=4))

        try:
            async with aiofiles.open(uploaded_path, "r", encoding="utf-8") as in_file:
                content = await in_file.read()
                if not content.strip():
                    raise ValueError("The JSON file is empty.")
                json_data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format in saved file.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
        
        user_response = [chat["user_message"] for chat in json_data.get("chat_data", [])]
        user_conversation = " ".join(user_response)

        if len(user_response) < 20:
            return {
                "Message": "Not enough user messages for personality trait analysis. Minimum 20 messages required."
            }

        username = json_data.get("username") \
        or next(
            (chat.get("username")
                for chat in json_data.get("chat_data", [])
                if chat.get("username")),
            "Unknown"
        )

        request_date = next(
            (chat.get("request_time").split("T")[0]
             for chat in json_data.get("chat_data", [])
             if "T" in chat.get("request_time", "")),
            ""
        )

        traits_report = os.path.join(REPORTS_DIR, f"{username}_Big_5_Personality_Report.pdf")

        detected_traits = Counter()
        SIMILARITY_THRESHOLD = 80
        MATCH_LIMIT = 3

        for phrase, trait in keyword_categories.items():
            matches = process.extract(
                phrase,
                user_conversation,
                scorer=fuzz.token_set_ratio,
                limit=MATCH_LIMIT
            )
            for match_text, score, _ in matches:
                if score >= SIMILARITY_THRESHOLD:
                    detected_traits[trait] += 1

        total_occurrences = sum(detected_traits.values()) or 1
        trait_percentages = {
            trait: (count / total_occurrences) * 100
            for trait, count in detected_traits.items()
        }

        explanation = await ensure_facet_availability(trait_percentages)

        class PersonalityPDF(FPDF):
            def header(self):
                self.set_fill_color(0, 102, 204)
                self.set_text_color(255, 255, 255)
                self.set_font("Arial", style="B", size=11)
                self.cell(0, 10, "Big 5 Personality Report", ln=True, align="C", fill=True)
                self.ln(4)
                self.set_text_color(0, 0, 0)

            def footer(self):
                self.set_y(-12)
                self.set_font("Arial", size=8)
                self.cell(0, 8, f"Page {self.page_no()}", align="C")

        pdf = PersonalityPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 6, "User", border=1, ln=0, align="L", fill=True)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, username, border=1, ln=1, align="L")

        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(30, 6, "Date", border=1, ln=0, align="L", fill=True)

        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 6, request_date, border=1, ln=1, align="L")

        pdf.ln(2)

        col_widths = [35, 10, 40, 30, 75]
        headers = ["Big Five Trait", "Score", "Key Insights", "Facet", "Interpretation"]

        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", style="B", size=9)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="C", fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=9)

        def add_trait_category(pdf, trait, score, key_insight, facets):
            pdf.set_font("Arial", size=7)

            trait = clean_text(trait)
            score = clean_text(score)
            key_insight = clean_text(key_insight)
            facets = {clean_text(k): clean_text(v) for k, v in facets.items()}

            key_insight_lines = pdf.multi_cell(col_widths[2], 4, key_insight, border=0, split_only=True)
            max_height = len(key_insight_lines) * 4

            facet_keys = list(facets.keys())
            facet_values = list(facets.values())

            x_trait, y_trait = pdf.get_x(), pdf.get_y()
            pdf.rect(x_trait, y_trait, col_widths[0], max_height)
            pdf.set_xy(x_trait, y_trait)
            pdf.multi_cell(col_widths[0], 4, trait, border=0)
            pdf.set_xy(x_trait + col_widths[0], y_trait)

            pdf.cell(col_widths[1], max_height, score, border=1, align="C")

            x_key, y_key = pdf.get_x(), pdf.get_y()
            pdf.multi_cell(col_widths[2], 4, key_insight, border=1)
            pdf.set_xy(x_key + col_widths[2], y_key)

            pdf.cell(col_widths[3], max_height, facet_keys[0], border=1)
            pdf.cell(col_widths[4], max_height, facet_values[0], border=1)
            pdf.ln()

            for i in range(1, len(facet_keys)):
                pdf.cell(col_widths[0], 4, "", border=1)
                pdf.cell(col_widths[1], 4, "", border=1)
                pdf.cell(col_widths[2], 4, "", border=1)
                pdf.cell(col_widths[3], 4, facet_keys[i], border=1)
                pdf.cell(col_widths[4], 4, facet_values[i], border=1)
                pdf.ln()

        for trait_data in explanation:
            trait_name, score, key_insight, facets = trait_data
            add_trait_category(pdf, trait_name, score, key_insight, facets)

        pdf.output(traits_report)
        pdf_url = f"{request.base_url}{traits_report}"

        return {
            "Message": "Personality trait report is created successfully.",
            "Pdf_url": pdf_url
        }

    except Exception as e:
        return {
            "Message": f"An error occurred: {str(e)}"
        }
