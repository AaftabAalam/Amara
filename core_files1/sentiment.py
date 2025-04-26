from fastapi import HTTPException
import matplotlib.pyplot as plt
from matplotlib import rcParams
from transformers import pipeline
import uuid
import os
import aiofiles
import unicodedata

UPLOAD_DIR = "uploads"
REPORTS_DIR = "sentiment_reports"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def normalize_text(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

async def evaluate_sentiments(request, data):
    try:
        unique_id = str(uuid.uuid4())
        uploaded_path = os.path.join(UPLOAD_DIR, f"{unique_id}.json")

        async with aiofiles.open(uploaded_path, "w", encoding="utf-8") as out_file:
            await out_file.write(data.model_dump_json(indent=2))

        username = data.username if data.username else "Unknown"

        feedback_responses = []
        for chat in data.chat_data:
            message = chat.user_message.strip()
            if message:
                if not message.endswith('.'):
                    message += '.'
                feedback_responses.append(normalize_text(message))


        if len(feedback_responses) < 20:
            return{
                "message": "Not enough user messages for sentiment analysis. Minimum 20 messages required."
            }

        if not feedback_responses:
            raise HTTPException(status_code=400, detail="No user messages found in the JSON data.")
    
        sentiments = []
        for response in feedback_responses:
            result = sentiment_pipeline(response)[0]
            label = result["label"]
            if label == "LABEL_0":
                score = -1
            elif label == "LABEL_1":
                score = 0
            else:
                score = 1
            
            sentiments.append(score)
            
        total = len(sentiments)
        positive_count = sentiments.count(1)
        neutral_count = sentiments.count(0)
        negative_count = sentiments.count(-1)

        positive_pct = (positive_count / total) * 100
        neutral_pct = (neutral_count / total) * 100
        negative_pct = (negative_count / total) * 100

        labels = ['Neutral Tones', 'Positive Tones', 'Negative Tones']
        sizes = [neutral_pct, positive_pct, negative_pct]
        colors = ['cornflowerblue', 'teal', 'lightskyblue']

        rcParams.update({'font.size': 14})

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_axes([0.08,   
                           0.15,   
                           0.45,  
                           0.70])  
        ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            wedgeprops={'edgecolor': 'white'},
            labels=None
        )
        ax.axis('equal')

        fig.suptitle(
            'SENTIMENT ANALYSIS',
            fontsize=16,
            fontweight='bold',
            y=0.75
        )
        x_text = 0.60
        y_positions = [0.60, 0.50, 0.40]  

        for pct, label, color, y in zip(
                [neutral_pct, positive_pct, negative_pct],
                labels,
                colors,
                y_positions):
            fig.text(
                x_text, y,
                f"{pct:.1f}%",
                ha='left', va='center',
                fontsize=12, color=color
            )
            fig.text(
                x_text, y - 0.05,
                label,
                ha='left', va='center',
                fontsize=12, color=color
            )

        chart_path = os.path.join(REPORTS_DIR, f"{username}_Sentiment_Analysis.pdf")
        fig.savefig(
            chart_path,
            format='pdf',
            bbox_inches='tight',
            pad_inches=0.1
        )
        plt.close(fig)
                
        sentiment_chart_url = f"{request.base_url}{chart_path}"
        return {
            "message": "File uploaded and sentiments calculated successfully.",
            "file_url": sentiment_chart_url,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
