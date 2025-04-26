from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form, WebSocket, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import subprocess
from typing import Any, Dict, List, Optional
import requests
import os
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from core_files.vidolysis import websocket_endpoint
import face_recognition
from PIL import Image
from io import BytesIO
import cv2
from core_files.utils import DocumentManager, VoiceAuthenticator, DialogflowRagWebhook,load_known_faces, save_known_faces
from core_files.Alertness import upload_raw_json as upload_raw_json_1
from core_files.Authenticity import upload_raw_json as upload_raw_json_2
from core_files.Emotion import upload_raw_json as upload_raw_json_3
from core_files.Opinion import upload_raw_json as upload_raw_json_4
from core_files.Sarcasm import upload_raw_json as upload_raw_json_5
from core_files.Detect_risk import upload_raw_json as upload_raw_json_6
from core_files.Openness import upload_raw_json as upload_raw_json_7
from core_files.logic import codes
from core_files.OSA_report import upload_raw_json as mix_pie
from core_files.llm_report import *
import uvicorn
from fastapi.staticfiles import StaticFiles
from core_files1.analyze import analyze_communication
# from core_files1.classify import *
from core_files1.summary import *
from core_files1.traits import *
from core_files1.describe import explain_code
from core_files1.hume_pdf import analyze_text, extract_text_from_pdf as extract_text_for_hume
from interview_analysis.detect_bias import *
from interview_analysis.detect_tones import measure_tone
from interview_analysis.transcribe import transcribe_audio
from interview_analysis.engagement import engagement_analysis
from interview_analysis.diversity import diversity_analysis
from interview_analysis.classify import classify_questions
from interview_analysis.clarity import analyze_transcript
from core_files1.sentiment import evaluate_sentiments

app = FastAPI()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/analysis_reports", StaticFiles(directory="analysis_reports"), name="reports")
app.mount("/actions_reports", StaticFiles(directory="actions_reports"), name="actions")
app.mount("/sentiment_reports", StaticFiles(directory="sentiment_reports"), name="sentiments")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

load_dotenv()

@app.post("/transcribe-audio/")
async def audio_transcribe(request: Request, file: UploadFile = File()):
    return await transcribe_audio(request, file)

@app.post("/engagement/")
async def analysis_engagement(request: Request, file: UploadFile = File(...)):
    return await engagement_analysis(request, file)

@app.post("/diversity/")
async def analysis_diversity(request: Request, file: UploadFile = File(...)):
    return await diversity_analysis(request, file)

@app.post("/detect-tone/")
async def tone_measure(request: Request, file: UploadFile = File(...)):
    return await measure_tone(request, file)

@app.post("/analyze-bias/")
async def bias_analyze(request: Request, file: UploadFile = File(...)):
    return await analyze_bias(request, file)

class ReportResponse(BaseModel):
    Message: str
    pdf_path: str

@app.post("/classify-questions/", response_model=ReportResponse)
async def question_classify(request: Request, file: UploadFile = File(...)) -> Dict[str, List[Dict[str, str]]]:
    return await classify_questions(request, file)

@app.post("/clarity/")
async def transcript_analyze(requst: Request, file: UploadFile = File(...)):
    return await analyze_transcript(requst, file)

@app.post("/hume-sentiments/")
async def analyze_pdf(file: UploadFile = File(...)):
    try:
        text = extract_text_for_hume(file.file)
        if not text.strip():
            return {"error": "No extractable text found in the PDF."}

        sentiment = await analyze_text(text)
        return {"file_name": file.filename, "sentiment": sentiment}

    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_traits/")
async def analyze_traits(request: Request):
    return await calculate_personality_trait(request)

@app.post("/summarize/")
async def summary(request: Request):
    try:
        data = await request.json()
        chat_data = data.get("chat_data", [])
        extracted_messages = [{"user_message": chat["user_message"], "bot_message": chat["bot_message"]} for chat in chat_data]
        summary = summarize(extracted_messages)
        return summary
    except Exception as e:
        return{
            "error":f"An error occurred:{str(e)}"
        }

class ChatData(BaseModel):
    turn_position: int
    request_time: str
    user_message: str
    bot_message: Optional[str] = None

class RequestData(BaseModel):
    username: str
    chat_data: List[ChatData]

@app.post("/analyze/")
async def analyze(request: Request, data: RequestData = Body(...)):
    return await analyze_communication(request, data)

@app.post("/sentiment/")
async def sentiment_calculate(request: Request, data: RequestData = Body(...)):
    return await evaluate_sentiments(request, data)


# @app.post("/classify-pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     temp_pdf_path = f"temp_{file.filename}"
#     with open(temp_pdf_path, "wb") as temp_file:
#         temp_file.write(await file.read())
#     extracted_text = read_json(temp_pdf_path)
#     os.remove(temp_pdf_path)
#     generated_response = format_prompt(extracted_text)
#     return {"generated_text": generated_response}

CREDENTIALS_PATH = 'mentalhealthcare-hbij-1160f988e5bd.json'
PERSIST_DIRECTORY = 'db'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class DocumentRequest(BaseModel):
    user_id: str
    document_name: str
    content: str 

class QueryResult(BaseModel):
    queryText: str
    parameters: Dict[str, Any]

class WebhookRequest(BaseModel):
    queryResult: QueryResult
    session: str

authenticator = VoiceAuthenticator()
doc_manager = DocumentManager()
dialogflow_handler = DialogflowRagWebhook(CREDENTIALS_PATH)

@app.websocket("/ws")
async def run_socket(websocket: WebSocket):
    try:
        await websocket_endpoint(websocket)
        return {"message": "Socket test executed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@app.get('/')
async def home():
    return "Server Running..!!"

@app.post("/dialogflow-webhook")
async def dialogflow_webhook(request: Request):
    try:
        req_data = await request.json()
        print(req_data)
    
        response = dialogflow_handler.handle_webhook(req_data)

        fulfillment_text = response.get("fulfillmentText", "Sorry, I could not process your request.")

        return {
                "fulfillmentResponse": {
                    "messages": [
                        {"text": {"text": [fulfillment_text]}}
                    ]
                },
                "sessionInfo": {
                    "parameters": {
                        "response_message": fulfillment_text
                    }   
                }
        }
    except Exception as e:
        return {
            "fulfillmentResponse": {
                "messages": [
                    {"text": {"text": [f"An error occurred: {str(e)}"]}}
                ]
            }
        }
    
@app.post('/store-document')
async def store_document(user_id: str = Form(...),
                         document_name: str = Form(...),
                         content: str = Form(None),
                         file: UploadFile = File(None)):
    try:
        if content and (content.startswith('http://') or content.startswith('https://')):
            try:
                response = requests.get(content)
                response.raise_for_status()
                
                content_type = response.headers.get('Content-Type', '')
                file_extension = content.split('.')[-1].lower()
                
                temp_file_path = f"./uploads/{document_name}.{file_extension}"
                
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(response.content)
                
                success, message = dialogflow_handler.doc_manager.store_document(
                    user_id=user_id,
                    document_name=document_name,
                    content=temp_file_path,
                    source=content
                )
                
                os.remove(temp_file_path)

            except requests.exceptions.RequestException as e:
                return {
                    "status": False,
                    "message": f"Error fetching URL content: {str(e)}"
                }
        
        elif file:
            temp_file_path = f"./uploads/{file.filename}"
            with open(temp_file_path, "wb") as temp_file:
                content = await file.read()
                temp_file.write(content)

            success, message = dialogflow_handler.doc_manager.store_document(
                user_id=user_id,
                document_name=document_name,
                content=temp_file_path,
                source='store-document'
            )
        elif content:
            success, message = dialogflow_handler.doc_manager.store_document(
                user_id=user_id,
                document_name=document_name,
                content=content,
                source='store-document'
            )        
        else:
            return {
                "status": False,
                "message": "No content provided"
            }
        if success:
            return {
                "status": True,
                "message": "Document stored successfully"
            }
        return {
            "status": False,
            "message": message
        }
    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }
        
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"

@app.post("/add_user/")
async def add_user(username: str = Form(...), file: UploadFile = Form(...)):
    """Add a new user with their voice recording."""
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not file:
        raise HTTPException(status_code=400, detail="Audio file is required")

    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension == "mp3":
            audio = AudioSegment.from_file(file.file, format="mp3").set_frame_rate(16000).set_channels(1)
            audio = np.array(audio.get_array_of_samples()) / 32767.0
        elif file_extension == "wav":
            audio, _ = sf.read(file.file)
            audio = audio / np.max(np.abs(audio))
        else:
            raise HTTPException(status_code=400, detail="Unsupported audio format. Use WAV or MP3.")

        filepath = authenticator.save_audio(audio, username)
        return {"message": f"Voice print saved for {username}", "file_path": filepath}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")


@app.post("/verify_user/")
async def verify_user(username: str = Form(...), file: UploadFile = Form(...)):
    """Verify a user with their current voice."""
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not file:
        raise HTTPException(status_code=400, detail="Audio file is required")
    try:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension == "mp3":
            audio = AudioSegment.from_file(file.file, format="mp3").set_frame_rate(16000).set_channels(1)
            audio = np.array(audio.get_array_of_samples()) / 32767.0
        elif file_extension == "wav":
            audio, _ = sf.read(file.file)
            audio = audio / np.max(np.abs(audio))
        else:
            raise HTTPException(status_code=400, detail="Unsupported audio format. Use WAV or MP3.")

        is_verified, similarity = authenticator.verify_user(username, audio)
        return {
            "verified": is_verified,
            "similarity_score": similarity,
            "message": "Verified" if is_verified else "Not Verified"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification error: {str(e)}")
    

@app.post("/encode_image/")
async def encode_face( image: UploadFile = File(...), 
    username: str = Form(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    
    image_data = await image.read()
    pil_image = Image.open(BytesIO(image_data))
    image_array = np.array(pil_image)

    face_encodings = face_recognition.face_encodings(image_array)
    if not face_encodings:
        raise HTTPException(status_code=400, detail="No face detected in the image.")

    known_encodings, known_usernames = load_known_faces()

    if username in known_usernames:
        indices_to_remove = [i for i, name in enumerate(known_usernames) if name == username]
        for index in reversed(indices_to_remove):
            del known_encodings[index]
            del known_usernames[index]

    known_encodings.append(face_encodings[0])
    known_usernames.append(username)

    save_known_faces(known_encodings, known_usernames)
    
    return {"status": True,
            "message": f"Encoded face for {username} and added to database."}

@app.post("/verify/")
async def verify_face( image: UploadFile = File(...), 
    username: str = Form(...)):
    known_encodings, known_usernames = load_known_faces()
    if not known_encodings:
        raise HTTPException(status_code=404, detail="No known faces found. Please encode faces first.")

    user_indices = [i for i, name in enumerate(known_usernames) if name == username]
    if not user_indices:
        raise HTTPException(status_code=404, detail=f"No face encodings found for username {username}")

    user_encodings = [known_encodings[i] for i in user_indices]

    image_data = await image.read()
    pil_image = Image.open(BytesIO(image_data))
    image_array = np.array(pil_image)

    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

    verification_results = []

    for face_encoding in face_encodings:

        matches = face_recognition.compare_faces(user_encodings, face_encoding)
        
        if any(matches):
           
            best_match_index = np.argmin(face_recognition.face_distance(user_encodings, face_encoding))
            if matches[best_match_index]:
                verification_results.append({
                    "username": username,
                    "match": True,
                    "confidence": 1 - face_recognition.face_distance(user_encodings, face_encoding)[best_match_index]
                })
        else:
            verification_results.append({
                "username": username,
                "match": False,
                "confidence": 0
            })

    if verification_results and any(result['match'] for result in verification_results):
        return {
            "status": True,
            "message": f"Face verification successful for {username}", 
            "verification_results": verification_results
        }
    else:
        return {
            "status": False,
            "message": f"No matching faces found for {username}", 
            "verification_results": verification_results
        }

@app.post("/upload-raw-json/")
async def upload_json(request: Request):
    try:
        try:
            result1 = await upload_raw_json_1(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_1: {str(e)}")

        try:
            result2 = await upload_raw_json_2(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_2: {str(e)}")

        try:
            result3 = await upload_raw_json_3(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_3: {str(e)}")

        try:
            result4 = await upload_raw_json_4(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_4: {str(e)}")

        try:
            result5 = await upload_raw_json_5(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_5: {str(e)}")

        try:
            result6 = await upload_raw_json_6(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_6: {str(e)}")

        try:
            result7 = await upload_raw_json_7(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in upload_raw_json_7: {str(e)}")
        
        try:
            result8 = await mix_pie(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in mix_pie: {str(e)}")

        return {
            "message": "File uploaded successfully.",
            "json_path": result1["json_path"],
            "pdf_path1": result1["pdf_path"],
            "pdf_path2": result2["pdf_path"],
            "pdf_path3": result3["pdf_path"],
            "pdf_path4": result4["pdf_path"],
            "pdf_path5": result5["pdf_path"],
            "pdf_path6": result6["pdf_path"],
            "pdf_path7": result7["pdf_path"],
            "pdf_path8": result8["pdf_path"]
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/upload_document/{user_id}")
async def add_docs(user_id: str, files: List[UploadFile] = File(...)):
    try:
        result = await upload_document(user_id, files)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except FileNotFoundError as fe:
        raise HTTPException(status_code=400, detail=str(fe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in upload document: str{(e)}")
    return result

@app.post("/ask_query/")
async def ask(query: QueryRequest):
    try:
        result = await ask_query(query)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(ve)}")
    except KeyError as ke:
        raise HTTPException(status_code=500, detail=f"Key error: {str(ke)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in ask_query: {str(e)}")
    return result

@app.get("/authenticity_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("authenticity_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")

@app.get("/openness_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("openness_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")

@app.get("/emotion_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("emotion_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")

@app.get("/opinion_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("opinion_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")

@app.get("/risk_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("risk_detection_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")

@app.get("/sarcasm_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("sarcasm_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")
    
@app.get("/alertness_logic/")
async def sarcasm_logic():
    try:
        function_code = codes.get("alertness_code", "")
        explanation = explain_code(function_code)
        if explanation:
            return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve function code: {str(e)}")


def run_uvicorn():
    command = [
        "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "9000",
        "--reload",
        "--ssl-certfile", "/etc/letsencrypt/live/amara.brenin.co/fullchain.pem",
        "--ssl-keyfile", "/etc/letsencrypt/live/amara.brenin.co/privkey.pem"
    ]
    subprocess.run(command)
    
#def run_vision_assistant(mode):
#    subprocess.Popen(['python','vision.py',mode])

if __name__ == '__main__':
    run_uvicorn()
    #vision_mode = 'start'

    #vision_thread = Thread(target=run_vision_assistant,args=(vision_mode,))
    #vision_thread.daemon = True
    #vision_thread.start()

    #uvicorn_thread = Thread(target=run_uvicorn)
    #uvicorn_thread.daemon = True
    #uvicorn_thread.start()

    #vision_thread.join()
    #uvicorn_thread.join()    
