import os
import cv2
import pyttsx3
import face_recognition
import numpy as np
import base64
import pickle
from fastapi import WebSocket, WebSocketDisconnect
from core_files.getEncode import auto_encode
from deepface import DeepFace
from dotenv import load_dotenv
from groq import Groq
import requests
import cv2
import mediapipe as mp
import numpy as np
import time
import logging
from datetime import datetime
from ultralytics import YOLO

engine = pyttsx3.init()
engine.setProperty('rate', 185)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[66].id)

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

def greeting(user_name):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate a random friendly greeting that directly includes the name {user_name}, without any additional context or explanation."
            }
        ],
        model="llama3-8b-8192",
    )
    message = chat_completion.choices[0].message.content
    return message

def feedback(emotion):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate a compassionate response about 1 to 2 lines for someone who is feeling {emotion}."
            }
        ],
        model="llama3-8b-8192",
    )
    message = chat_completion.choices[0].message.content
    return message

def load_known_faces():
    try:
        with open('face_encodings.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("Error: The file 'face_encodings.pkl' does not exist.")
        return [], []
    except Exception as e:
        print(f"An error occurred while loading the pickle file: {e}")
        return [], []
    

API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

known_face_encodings = []

async def analyze_image(base64_image: str) -> str:
    data = {
        "model": "llama-3.2-11b-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze the image and provide a brief, direct compliment to the person in the image. Compliment the person on their attire. Address the person directly in the second person (e.g., 'You look great in that shirt!' or 'You have such a warm smile!'). Do not refer to the person in third person (e.g., 'the person looks good'). Also, acknowledge their surroundings and how the background enhances the overall atmosphere, but speak directly to the person about how their surroundings complement them. Keep the compliment very short and natural and very important do not add your additional comments and explantion."},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    },
                ],
            }
        ],
        "max_tokens": 124,
    }
    
    response = requests.post(GROQ_API_URL, headers=HEADERS, json=data)
    json_response = response.json()
    return json_response["choices"][0]["message"]["content"]


class AttentionTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, min_detection_confidence=0.6, min_tracking_confidence=0.6
        )

        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        self.phone_detector = YOLO("yolov8n.pt")

        # Core tracking parameters
        self.attention_threshold = 0.81
        self.attention_window = 5
        self.attention_history = []
        self.last_alert_time = 0
        self.alert_cooldown = 10

        # Mouth landmarks for talking detection
        self.MOUTH = [61, 291, 39, 181, 0, 17, 269, 405]
        self.mouth_history = []
        self.mouth_movement_threshold = 0.08

        # Eye landmarks
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.NOSE = 1

        logging.basicConfig(filename='attention_log.txt', level=logging.INFO, 
                          format='%(asctime)s - %(message)s')

    def calculate_eye_aspect_ratio(self, eye_landmarks):
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        return (v1 + v2) / (2.0 * h)

    def calculate_mouth_aspect_ratio(self, mouth_landmarks):
        vertical1 = np.linalg.norm(mouth_landmarks[1] - mouth_landmarks[7])
        vertical2 = np.linalg.norm(mouth_landmarks[2] - mouth_landmarks[6])
        horizontal = np.linalg.norm(mouth_landmarks[0] - mouth_landmarks[4])
        return (vertical1 + vertical2) / (2.0 * horizontal)

    def detect_phone(self, frame):
        results = self.phone_detector(frame)
        phone_detected = False
        phone_box = None

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                if cls == 67:  # cell phone class
                    phone_detected = True
                    phone_box = box.xyxy[0].tolist()
                    break
        return phone_detected, phone_box

    def detect_talking(self, frame, face_landmarks):
        mouth_points = np.array([[face_landmarks.landmark[i].x * frame.shape[1], 
                                face_landmarks.landmark[i].y * frame.shape[0]] 
                                for i in self.MOUTH])
        mar = self.calculate_mouth_aspect_ratio(mouth_points)

        current_time = time.time()
        self.mouth_history.append((current_time, mar))
        self.mouth_history = [(t, s) for t, s in self.mouth_history 
                            if current_time - t <= self.attention_window]

        if len(self.mouth_history) > 1:
            mar_change = abs(self.mouth_history[-1][1] - self.mouth_history[0][1])
            return mar_change > self.mouth_movement_threshold
        return False

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = self.face_detector.process(frame_rgb)
        mesh_results = self.face_mesh.process(frame_rgb)
        
        phone_detected, phone_box = self.detect_phone(frame)
        
        attention_data = {
            "timestamp": datetime.now().isoformat(),
            "phone_detected": phone_detected,
            "phone_box": phone_box,
            "is_talking": False,
            "people_count": 0
        }

        if face_results.detections:
            attention_data["people_count"] = len(face_results.detections)

        if mesh_results.multi_face_landmarks:
            face_landmarks = mesh_results.multi_face_landmarks[0]

            left_eye = np.array([[face_landmarks.landmark[i].x * frame.shape[1], 
                                face_landmarks.landmark[i].y * frame.shape[0]] 
                                for i in self.LEFT_EYE])
            right_eye = np.array([[face_landmarks.landmark[i].x * frame.shape[1], 
                                face_landmarks.landmark[i].y * frame.shape[0]] 
                                for i in self.RIGHT_EYE])

            left_ear = self.calculate_eye_aspect_ratio(left_eye)
            right_ear = self.calculate_eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            ear = np.clip(ear / 0.35, 0, 1)

            attention_data["is_talking"] = bool(self.detect_talking(frame, face_landmarks))
            attention_data["eye_aspect_ratio"] = float(ear)

            nose = face_landmarks.landmark[self.NOSE]
            gaze_deviation = abs(nose.x - 0.5) * 2
            gaze_score = max(0, 1 - gaze_deviation)
            attention_score = (0.6 * ear) + (0.4 * gaze_score)

            if attention_data["people_count"] > 1:
                attention_score *= 0.7
            if phone_detected:
                attention_score *= 0.5

            attention_data["attention_score"] = float(attention_score)

        attention_data = {k: (v.item() if isinstance(v, (np.bool_, np.float32, np.float64)) else v) for k, v in attention_data.items()}
        
        return attention_data

tracker = AttentionTracker()

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted.")

    faces_dir = 'faces/'
    os.makedirs(faces_dir, exist_ok=True)

    if not os.path.exists('face_encodings.pkl'):
        auto_encode()

    known_face_encodings, known_face_names = load_known_faces()

    greeted_names = set()
    person_emotion_spoken = {}
    described_people = {}

    while True:
        try:
            frame_json = await websocket.receive_json()
            frame_str = frame_json.get("frame", "")
            frame_parts = frame_str.split(",")

            if len(frame_parts) > 1:
                frame_data = frame_parts[1]
            else:
                await websocket.send_json({"error": "Invalid frame data format"})
                continue

            frame_bytes = base64.b64decode(frame_data)
            np_data = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)

            if frame is None:
                print("Empty frame received, skipping...")
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings_in_frame = face_recognition.face_encodings(rgb_frame, face_locations)

            attention_results = tracker.process_frame(frame)

            response_data = {"attention_tracking": attention_results, "descriptions":[]} 

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings_in_frame):
                if not face_encodings_in_frame:
                    print("No faces encoded in the frame.")
                    continue
                
                if not known_face_encodings:
                    print("No known face encodings available.")
                    continue

                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                # name = "Unknown"
                # if matches and any(matches):
                #     best_match_index = np.argmin(face_recognition.face_distance(known_face_encodings, face_encoding))
                #     name = known_face_names[best_match_index]

                if not any(matches):
                    unknown_count = sum(1 for name in known_face_names if name.startswith("Unknown"))
                    name = f"Unknown{unknown_count + 1}"
                    known_face_encodings.append(face_encoding)
                    known_face_names.append(name)
                else:
                    best_match_index = np.argmin(face_recognition.face_distance(known_face_encodings, face_encoding))
                    name = known_face_names[best_match_index]

                if name not in greeted_names:
                    greeting_message = greeting(name)
                    greeted_names.add(name)
                    response_data["greeting"] = greeting_message

                try:
                    results = DeepFace.analyze(frame[top:bottom, left:right], actions=["emotion"], enforce_detection=False)
                    if isinstance(results, list) and results:
                        emotion = results[0]["dominant_emotion"]
                    elif isinstance(results, dict) and "dominant_emotion" in results:
                        emotion = results["dominant_emotion"]
                    else:
                        emotion = "unknown"
                except Exception as e:
                    print(f"Error analyzing emotion: {e}")
                    emotion = "unknown"

                if name not in person_emotion_spoken:
                    emotion_message = feedback(emotion)
                    person_emotion_spoken[name] = emotion
                    response_data["emotion_feedback"] = emotion_message

                if name not in described_people:
                    frame_resized = cv2.resize(frame, (400, 300))
                    success, buffer = cv2.imencode(".png", frame_resized)
                    if not success:
                        print("Error encoding image")
                        continue
                    base64_resized_image = base64.b64encode(buffer).decode("utf-8")
                    description = await analyze_image(base64_resized_image)
                    described_people[name] = description

                response_data["descriptions"].append({
                    "name": name,
                    "description": described_people[name]
                })

                # if True not in matches:
                #     known_face_encodings.append(face_encoding)
            await websocket.send_json(response_data)

        except WebSocketDisconnect:
            print('Client Disconnected.')
            break
        except Exception as e:
            await websocket.send_json({"error": str(e)})