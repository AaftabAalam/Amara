import pdfplumber
import os
from transformers import pipeline
import json

model_name = "rohangbs/fine-tuned-aftab"
pipe = pipeline(task="text-generation", model=model_name, tokenizer=model_name, device_map="auto")

def read_json(json_path: str):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    chat_messages = []
    if "chat_data" in data:
        for chat in data["chat_data"]:
            user_msg = chat.get("user_message", "").strip()
            bot_msg = chat.get("bot_message", "").strip()
            chat_messages.append(f"User: {user_msg}\nBot: {bot_msg}\n")

    extracted_text = "\n".join(chat_messages)
    return extracted_text.strip()


def format_prompt(text: str):
    prompt = f"""In the given data conclude in one or two lines about what is being addressed or concern or talked upon topic, subject etc and do not mention from the content itself but explain from the content about the topics or concerns.
    Remember not to add your comments or explanation.
    This is the incoming data from which you need to perform the task:
    {text}
    ### Response:
    """
    outputs = pipe(
        prompt,
        max_new_tokens=30,
        do_sample=True,
        temperature=0.8,
        top_p=0.9
    )
    result = outputs[0]["generated_text"].strip()
    
    if "### Response:" in result:
        generated_text = result.split("### Response:")[1].strip()
    else:
        generated_text = result
    return generated_text