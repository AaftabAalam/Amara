import json

def read_json(json_input):
    if isinstance(json_input, dict):
        data = json_input 
    else:
        with open(json_input, "r", encoding="utf-8") as file:
            data = json.load(file)

    chat_messages = []
    if "chat_data" in data:
        for chat in data["chat_data"]:
            user_msg = chat.get("user_message", "").strip()
            bot_msg = chat.get("bot_message", "").strip()
            chat_messages.append(f"User: {user_msg}\nBot: {bot_msg}\n")

    extracted_text = "\n".join(chat_messages)
    return extracted_text.strip()