import matplotlib.pyplot as mplt
from core_files.metrics1 import *
from pathlib import Path
from core_files.json_extraction import load_and_process_json
from matplotlib.backends.backend_pdf import PdfPages
from core_files.functions import UPLOAD_DIR
import json
import os
from fastapi import Request

async def upload_raw_json(request: Request):
    try:
        data = await request.json()
    
        if "reference_id" not in data:
            return {"error": "Reference ID not found in the JSON data"}

        if "json_data" not in data:
            return {"error": "Json_data key is not found in the request."}

        reference_id = data["reference_id"]
        json_data = data["json_data"]
        file_name = "data.json"

        UPLOAD_DIR = "uploads/"+reference_id
        Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        chat_data = load_and_process_json(file_path)
        result = detect_sarcasm(chat_data, sarcasm_indicators, exaggeration_phrases, contradictory_phrases)

        categories = [key for key in result if isinstance(result[key], (int, float))]
        values = [result[key] for key in categories]
        
        included_labels = {"Sarcasm Indicators", "Exaggerations", "Contradictions"}

        filtered_categories = [cat for cat in categories if cat in included_labels]
        filtered_values = [val for cat, val in zip(categories, values) if cat in included_labels]

        pdf_path = "uploads/"+reference_id+"/_Sarcasm_Report.pdf"

        with PdfPages(pdf_path) as pdf:
            # Pie Chart
            if sum(values) > 0:
                threshold = 5
                explode = [0.1 if (v / sum(filtered_values)) * 100 < threshold else 0 for v in filtered_values]

                total = sum(filtered_values)
                percentages = [(v / total) * 100 for v in filtered_values]

                legend_labels = [
                    f"{cat} ({pct:.1f}%)" 
                    for cat, pct in zip(filtered_categories, percentages) 
                ]

                colours = ["#6BCB77", "#4D96FF", "#FFD93D"]
                mplt.figure(figsize=(6, 6))
                wedges, texts = mplt.pie(
                    filtered_values,
                    startangle=60,
                    labeldistance=1.5,
                    explode=explode,
                    colors=colours[:len(filtered_values)]
                )

                mplt.legend(wedges, legend_labels, title="Categories", loc="best", bbox_to_anchor=(1, 0.49))
                mplt.title('Sarcasm Report')
                mplt.tight_layout()
                mplt.subplots_adjust(top=0.80, bottom=0.30)
                pdf.savefig()
                mplt.close()
            else:
                mplt.figure(figsize=(6,6))
                mplt.text(0.5, 0.5, "No data to display", ha="center", va="center", fontsize=12)
                mplt.axis("off")
                mplt.title("Sarcasm Report")
                pdf.savefig()
                mplt.close()

        return {
            "json_path":f"{request.base_url}"+file_path,
            "pdf_path": f"{request.base_url}"+pdf_path
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        return False