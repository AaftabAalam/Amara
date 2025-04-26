import json

def load_and_process_json(file_path):
    try:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            raise ValueError(f"The file at {file_path} was not found.")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {file_path}: {str(e)}")

        try:
            chat_data = ""
            for key, value in data.items():
                if isinstance(value, str):
                    chat_data += " " + value
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str):
                            chat_data += " " + sub_value
                        elif isinstance(sub_value, list):
                            chat_data += " " + " ".join(map(str, sub_value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            chat_data += " " + item
                        elif isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                if isinstance(sub_value, str):
                                    chat_data += " " + sub_value
                                elif isinstance(sub_value, list):
                                    chat_data += " " + " ".join(map(str, sub_value))
            
            return chat_data.strip()
        except Exception as e:
            raise ValueError(f"Error processing JSON data: {str(e)}")

    except ValueError as ve:
        raise ve
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {str(e)}")
