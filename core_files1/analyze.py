import os
import uuid
import pdfplumber
import aiofiles
from fastapi import HTTPException
from fpdf import FPDF
import unicodedata
from groq import Groq
import json
import re
from dotenv import load_dotenv


load_dotenv()

UPLOAD_DIR = "uploads"
REPORTS_DIR = "analysis_reports"
ACTION_DIR = "actions_reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(ACTION_DIR, exist_ok=True)

def analysis(data):
    prompt = f"""
    You are an advanced AI tasked with analyzing a set of feedback and communication data for a single user, focusing on both **general feedback analysis** and **trend analysis**.
    1. **Feedback Analysis**:
        Analyze the following feedback responses and identify the most common themes, key points, and recurring topics mentioned across the feedback. Summarize the most important aspects that are commonly discussed in a clear and concise way. 

        Here are the feedback data:
        {data}

        Focus on identifying without discarding any point:
        - **primary topics** that are mentioned in most feedback.
        - **Recurring qualities** or features of the course that are praised.
        - Any **important takeaways** or shared opinions expressed in the responses.

    2. **Trend Analysis**:
        You also need to identify recurring trends and themes without discarding any mentioned posints such as:
        - **Workload concerns**
        - **Communication issues**
        - **Suggestions**
    
        - **Important Point**:
        You should explain all the points that at last we get that tells everything about the data in short points.

        Please provide an analysis by extracting key themes, categorizing them, and highlighting any significant patterns in the text provided. Below is the incoming communication data:

        {data}

        Provide the recurring trends and themes with explanations for each category.
        Always generate heading with 
        Remember not to add your comments or explanation or any other part that is not mentioned to generate just explain the mentioned things.
        Provide the output content in a well structured pdf format in section wise with headings.
"""
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def action(data):
    prompt = f"""
    You are an expert in workplace analysis and management optimization. Your task is to analyze and rank common workplace issues based on their **frequency** and **urgency**. The key focus areas include:

    - Workload management  
    - Patient care  
    - Team collaboration  

    ### **Instructions:**
    - **Identify and rank issues**: Evaluate the most common challenges in these areas based on their impact and urgency.  
    - **Summarize results**: Provide a concise yet detailed summary of the key findings.  
    - **Prioritize action items**: Recommend the top priorities for management to address, ensuring optimal efficiency and effectiveness.  

    ### **Output Format:**  
    Provide a **structured summary report** with:  
    - **Key Findings**: A ranked list of the most pressing issues.  
    - **Action Items**: Specific, practical recommendations for management.  
    - **Priority Level**: Categorization of issues as High, Medium, or Low priority.  

    Ensure clarity, data-driven insights, and actionable recommendations.
    This is the data : {data}

    Provide the output content in a well structured pdf format in section wise with headings. Remember not to add your comments or explanation just explain the mentioned things.
"""
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


## analysis report code
class CustomPDF(FPDF):
    def header(self):
        pass

def print_table_header(pdf, col_widths):
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(col_widths[0], 10, "Categories", border=1, align='C', fill=True)
    pdf.cell(col_widths[1], 10, "Details",    border=1, align='C', fill=True)
    pdf.ln()
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)

def generate_analysis_report(data, username, chat_date):
    report_path = os.path.join(REPORTS_DIR, f"{username}_Interaction_Breakdown_Report.pdf")

    pdf = CustomPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(0, 12, "Interaction Breakdown Report", border=1, ln=True, align='C', fill=True)
    pdf.ln(4)

    label_w = 30
    value_w = pdf.w - pdf.l_margin - pdf.r_margin - label_w

    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(label_w, 10, "User", border=1, align='L', fill=True)

    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(value_w, 10, username, border=1, ln=True, align='L', fill=False)

    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(label_w, 10, "Date", border=1, align='L', fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(value_w, 10, chat_date, border=1, ln=True, align='L', fill=False)
    pdf.ln(6)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    
    col_widths = [50, 140]
    print_table_header(pdf, col_widths)
    
    current_category = ""
    first_entry = True

    for line in data.splitlines():
        line = line.strip()
        if not line:
            continue

        if re.match(r"^[=]+$", line):
            continue

        header_match = re.match(r"^\*\*(.+?)\*\*$", line)
        if header_match:
            current_category = header_match.group(1).strip()
            first_entry = True
            continue

        if line.startswith("## "):
            heading = line[3:].strip()
            current_category = heading
            first_entry = True
            continue

        if line.startswith("### "):
            current_category = line[4:].strip()
            first_entry = True
            continue

        if re.match(r"^[\*\+\-]\s+", line):
            content = re.sub(r"^[\*\+\-]\s+", "", line)
            if re.match(r"^\*\*.*\*\*:\s*$", content):
                cat_match = re.match(r"^\*\*(.*?)\*\*:\s*$", content)
                if cat_match:
                    current_category = cat_match.group(1).strip()
                    first_entry = True
                continue
            else:
                if ":" in content:
                    parts = content.split(":", 1)
                    key_point = parts[0].strip()
                    details = parts[1].strip()
                else:
                    key_point = ""
                    details = content

            key_point = re.sub(r"^[#\*\+\-\s]+", "", key_point)
            details = re.sub(r"^[#\*\+\-\s]+", "", details)

            if current_category.lower() != "important points":
                if key_point.startswith("**") and key_point.endswith("**"):
                    key_point = key_point[2:-2].strip()
        
        elif re.match(r"^\d+\.", line):
            if current_category.lower() == "important points":
                cleaned = re.sub(r"^\d+\.\s*[#\*\+\-\s]+", "", line)
                key_point = ""
                details = cleaned
            else:
                m = re.match(r"^\d+\.\s*(\*\*.*?\*\*)\s*:\s*(.*)$", line)
                if m:
                    key_point = m.group(1).strip()
                    details = m.group(2).strip()
                else:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        key_point = parts[0].strip()
                        details = parts[1].strip()
                    else:
                        key_point = line
                        details = ""
                if key_point.startswith("**") and key_point.endswith("**"):
                    key_point = key_point[2:-2].strip()
        else:
            continue
        
        key_point = re.sub(r'\*+$', '', key_point).strip()

        combined = (
            f"{key_point}: {details}"
            if key_point and details
            else (key_point or details)
        ).strip()

        wrapped = pdf.multi_cell(col_widths[1], 10, combined, border=0, split_only=True)
        num_lines = max(len(wrapped), 1)
        row_height = num_lines * 10

        if pdf.get_y() + row_height > pdf.page_break_trigger:
            pdf.add_page()
            print_table_header(pdf, col_widths)

        y0 = pdf.get_y()

        cat_text = current_category if first_entry else ""
        pdf.cell(col_widths[0], row_height, cat_text, border=1, align='C')

        x1, y1 = pdf.get_x(), y0
        pdf.multi_cell(col_widths[1], 10, combined, border=0)
        pdf.set_xy(x1, y1)
        pdf.rect(x1, y1, col_widths[1], row_height)

        pdf.set_y(y0 + row_height)
        first_entry = False

    pdf.output(report_path)
    return report_path
## Analysis code over

#Action report code
def clean_text(text):
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def get_multi_cell_height(pdf, w, txt, cell_line_height):
    txt = clean_text(txt)
    words = txt.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line != "" else "") + word
        if pdf.get_string_width(test_line) <= w:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return len(lines) * cell_line_height, lines

def add_table_dynamic(pdf, header, data, col_widths, cell_line_height=10):
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    for col, width in zip(header, col_widths):
        pdf.cell(width, cell_line_height, col, 1, 0, 'C', fill=True)
    pdf.ln(cell_line_height)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", "", 12)
    for row in data:
        max_height = 0
        cell_lines = []
        for i, cell in enumerate(row):
            text = clean_text(str(cell))
            height, lines = get_multi_cell_height(pdf, col_widths[i], text, cell_line_height)
            cell_lines.append(lines)
            if height > max_height:
                max_height = height

        if pdf.get_y() + max_height > pdf.page_break_trigger:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(0, 102, 204)
            pdf.set_text_color(255, 255, 255)
            for col, width in zip(header, col_widths):
                pdf.cell(width, cell_line_height, col, 1, 0, 'C', fill=True)
            pdf.ln(cell_line_height)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 12)

        x_start = pdf.get_x()
        y_start = pdf.get_y()
        for i, cell in enumerate(row):
            x_current = pdf.get_x()
            y_current = pdf.get_y()
            pdf.multi_cell(col_widths[i], cell_line_height, clean_text(str(cell)), border=0)
            pdf.set_xy(x_current + col_widths[i], y_current)

        x_row_end = x_start
        for i, width in enumerate(col_widths):
            pdf.rect(x_row_end, y_start, width, max_height)
            x_row_end += width
        pdf.set_xy(x_start, y_start + max_height)

def add_table(pdf, header, data, col_widths, cell_line_height=10):
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    for col, width in zip(header, col_widths):
        pdf.cell(width, cell_line_height, col, 1, 0, 'C', fill=True)
    pdf.ln(cell_line_height)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", "", 12)
    for row in data:
        max_height = 0
        cell_heights = []
        for i, cell in enumerate(row):
            text = clean_text(str(cell))
            height, lines = get_multi_cell_height(pdf, col_widths[i], text, cell_line_height)
            cell_heights.append((height, lines))
            if height > max_height:
                max_height = height

        if pdf.get_y() + max_height > pdf.page_break_trigger:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(0, 102, 204)
            pdf.set_text_color(255, 255, 255)
            for col, width in zip(header, col_widths):
                pdf.cell(width, cell_line_height, col, 1, 0, 'C', fill=True)
            pdf.ln(cell_line_height)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 12)

        x_start = pdf.get_x()
        y_start = pdf.get_y()

        for i, cell in enumerate(row):
            x_current = pdf.get_x()
            y_current = pdf.get_y()
            pdf.multi_cell(col_widths[i], cell_line_height, clean_text(str(cell)), border=0)
            pdf.set_xy(x_current + col_widths[i], y_current)

        x_row_end = x_start
        for i, width in enumerate(col_widths):
            pdf.rect(x_row_end, y_start, width, max_height)
            x_row_end += width
        pdf.set_xy(x_start, y_start + max_height)

def create_pdf_tables(table1_data, table2_data, username, chat_date):
    report_path = os.path.join(ACTION_DIR, f"{username}_Intelligence_Interaction_Report.pdf")

    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, 'Intelligence Interaction Report', 1, 1, 'C', fill=True)
    pdf.ln(2)

    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 10, 'User', 1, 0, 'L', fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, username, 1, 1, 'L')

    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 10, 'Date', 1, 0, 'L', fill=True)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, chat_date, 1, 1, 'L')
    pdf.ln(5)

    header1 = ["Section", "Key Points", "Details"]
    col_widths1 = [40, 50, 100]
    
    add_table_dynamic(pdf, header1, table1_data, col_widths1, cell_line_height=10)
    
    pdf.ln(10)

    header2 = ["Priority", "Level"]
    col_widths2 = [95, 95]
    
    add_table(pdf, header2, table2_data, col_widths2, cell_line_height=10)
    
    pdf.output(report_path)
    return report_path

def parse_markdown_to_tables(data):
    data = clean_text(data)
    lines = data.splitlines()
    sections = {}
    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("## "):
            header = line[3:].strip()
            header = re.sub(r'^\*\*(.*?)\*\*$', r'\1', header)
            current_section = header
            sections[current_section] = []
        elif current_section:
            sections[current_section].append(line)
    for sec in sections:
        sections[sec] = "\n".join(sections[sec]).strip()
    
    table1_data = []
    for sec in ["Key Findings", "Action Items"]:
        if sec in sections:
            content = sections[sec]
            section_rows = []
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('*'):
                    cleaned = re.sub(r'^(\d+\.\s*|\-\s*|\*\s*)', '', line)
                    parts = cleaned.split(":", 1)
                    if len(parts) == 2:
                        key_point = re.sub(r'\*\*(.*?)\*\*', r'\1', parts[0].strip())
                        details = parts[1].strip()
                        section_rows.append((sec, key_point, details))
            if section_rows:
                table1_data.append(section_rows[0])
                for row in section_rows[1:]:
                    table1_data.append(("", row[1], row[2]))
    
    table2_data = []
    priority_section = None
    for key in sections:
        if key.lower().startswith("priority level"):
            priority_section = key
            break
    if priority_section:
        content = sections[priority_section]
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('*'):
                cleaned = re.sub(r'^(\d+\.\s*|\-\s*|\*\s*)', '', line)
                parts = cleaned.split(":", 1)
                if len(parts) == 2:
                    priority = re.sub(r'\*\*(.*?)\*\*', r'\1', parts[0].strip())
                    level = parts[1].strip()
                    table2_data.append((priority, level))
    return table1_data, table2_data
## action report code over

async def analyze_communication(request, data):
    try:
        unique_id = str(uuid.uuid4())
        uploaded_path = os.path.join(UPLOAD_DIR, f"{unique_id}.json")

        content = json.dumps(data.dict()).encode("utf-8")
        async with aiofiles.open(uploaded_path, "wb") as out_file:
            await out_file.write(content)

        with open(uploaded_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        def normalize_text(text):
            return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

        username = data.get("username", "Unknown")
        chat_data = data.get("chat_data", [])
        if chat_data:
            first = chat_data[0]
            rt = first.get("request_time", "")
            chat_date = rt.split("T", 1)[0] if "T" in rt else ""
        else:
            chat_date = ""

        feedback_responses = []
        for chat in data.get("chat_data", []):
            message = chat.get("user_message", "").strip()
            if message:
                if not message.endswith('.'):
                    message += '.'
                feedback_responses.append(normalize_text(message))

        if len(feedback_responses) < 20:
            return {
                "message": "Not enough user messages for analysis. Minimum 20 messages required."
            }
        
        if not feedback_responses:
            raise HTTPException(status_code=400, detail="No user messages found in the JSON data.")

        analysis_response = analysis(feedback_responses)
        analysis_response = "\n".join([line.strip() for line in analysis_response.split("\n") if line.strip()])
        analysis_report_path = generate_analysis_report(analysis_response, username, chat_date)

        with pdfplumber.open(analysis_report_path) as file:
           report_data = "\n".join([page.extract_text() or "" for page in file.pages])

        action_response = action(report_data)
        table1_data, table2_data = parse_markdown_to_tables(action_response)
        action_report_path = create_pdf_tables(table1_data, table2_data, username, chat_date)

        analysis_report_url = f"{request.base_url}{analysis_report_path}"
        action_report_url = f"{request.base_url}{action_report_path}",

        return {
            "message": "Processing completed",
            "analysis_report_url": analysis_report_url,
            "action_report_url": action_report_url[0],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})