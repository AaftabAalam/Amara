import os
from fastapi import HTTPException
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

def summarize(data):
    prompt = f"""
    You are an advanced AI language model trained to summarize content efficiently.
    Given the following input, generate a concise and informative summary that captures the key ideas, essential details, and main takeaways while maintaining clarity and coherence.
    Avoid redundancy and focus on the most important points. Remember not to add your comments or explanation.

    Incoming data:
    {data}
    """

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gemma2-9b-it",
        )
        return {
            "summary":chat_completion.choices[0].message.content
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {str(e)}")
