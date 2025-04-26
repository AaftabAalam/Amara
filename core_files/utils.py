from google.oauth2 import service_account
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import numpy as np
import requests
from PyPDF2 import PdfReader
import face_recognition
import pickle
import torch
from transformers import Wav2Vec2FeatureExtractor, WavLMModel
import torch.nn.functional as F
import scipy.io.wavfile as wav_io
import soundfile as sf
from pydub import AudioSegment
from dotenv import load_dotenv
load_dotenv()

# Constants
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
config = {'UPLOAD_FOLDER': UPLOAD_FOLDER}

CREDENTIALS_PATH = 'mentalhealthcare-hbij-1160f988e5bd.json'
PERSIST_DIRECTORY = 'db'
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class DocumentManager:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def fetch_content_from_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  
            return response.text
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error fetching content from URL: {str(e)}")

    def read_file_content(self, file_path):
        if not os.path.exists(file_path):
            raise ValueError(f"File {file_path} not found.")

        if file_path.endswith(".pdf"):
            return self._read_pdf_content(file_path)
        elif file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    def _read_pdf_content(self, file_path):
        try:
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            return content
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")

    def store_document(self, user_id, document_name, content, source=None):
        try:
            if content.startswith("http://") or content.startswith("https://"):
                content = self.fetch_content_from_url(content)

            elif os.path.exists(content):
                content = self.read_file_content(content)

            persist_dir = f"{PERSIST_DIRECTORY}/{user_id}/{document_name}"
            os.makedirs(persist_dir, exist_ok=True)

            texts = self.text_splitter.split_text(content)

            metadatas = [{
                'chunk_id': i,
                'document_name': document_name,
                'source': source,
                'user_id': user_id
            } for i in range(len(texts))]

            vector_store = Chroma.from_texts(
                texts=texts,
                embedding=embeddings,
                metadatas=metadatas,
                persist_directory=persist_dir
            )
            vector_store.persist()

            return True, f"Successfully stored document with {len(texts)} chunks"

        except Exception as e:
            return False, str(e)

class VoiceAuthenticator:
    def __init__(self, model_name="microsoft/wavlm-base"):
        self.user_dir = "user_voiceprints"
        os.makedirs(self.user_dir, exist_ok=True)

        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(model_name)
        self.model = WavLMModel.from_pretrained(model_name)

    def save_audio(self, audio: np.ndarray, username: str):
        filepath = os.path.join(self.user_dir, f"{username}_voiceprint.wav")
        wav_io.write(filepath, 16000, (audio * 32767).astype(np.int16))
        return filepath

    def extract_embeddings(self, audio: np.ndarray):
        inputs = self.feature_extractor(audio, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(inputs.input_values)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings

    def verify_user(self, username: str, current_audio: np.ndarray, threshold=0.88):
        reference_path = os.path.join(self.user_dir, f"{username}_voiceprint.wav")
        if not os.path.exists(reference_path):
            raise FileNotFoundError(f"No voice print found for {username}")
        
        reference_audio, _ = sf.read(reference_path)
        reference_embedding = self.extract_embeddings(reference_audio)
        current_embedding = self.extract_embeddings(current_audio)

        reference_embedding = F.normalize(reference_embedding, dim=1)
        current_embedding = F.normalize(current_embedding, dim=1)
        similarity = F.cosine_similarity(reference_embedding, current_embedding).item()

        return similarity >= threshold, similarity

class DialogflowRagWebhook:
    def __init__(self, credentials_path):
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        self.project_id = 'mentalhealthcare-hbij'
        self.location_id = 'asia-south1'
        self.agent_id = '2621de8c-e7ef-4f98-ab8f-81bb8cdb29fe'
        self.doc_manager = DocumentManager()

    def get_rag_response(self, user_id, document_name, question):
        try:
            vector_store = Chroma(
                persist_directory=f"{PERSIST_DIRECTORY}/{user_id}/{document_name}",
                embedding_function=embeddings
            )
            
            chat_model = ChatGroq(
                groq_api_key=os.getenv("GROQ_API_KEY"),
                model_name="gemma2-9b-it"
            )
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=chat_model,
                retriever=vector_store.as_retriever(),
                return_source_documents=True
            )
            
            response = qa_chain({"question": question, "chat_history": []})
            
            return {
                'answer': response['answer'],
                'sources': [str(doc.metadata) for doc in response['source_documents']]
            }
        
        except Exception as e:
            return {
                'error': f'Error processing RAG query: {str(e)}'
            }

    def handle_webhook(self, webhook_request):
        try:
            query_text = webhook_request.get('sessionInfo', {}).get('parameters', {}).get('query_text', '')
            session_info = webhook_request.get('sessionInfo', {})
            user_id = session_info.get('session', '').split('/')[-1]
            parameters = session_info.get('parameters', {})
            document_name = parameters.get('document_name', '')

            if not document_name:
                return {
                    'fulfillmentText': 'Please specify which document you want to query.',
                    'sources': None
                }

            rag_response = self.get_rag_response(user_id, document_name, query_text)

            if 'error' in rag_response:
                fulfillment_text = rag_response['error']
                sources = None
            else:
                fulfillment_text = rag_response['answer']
                sources = rag_response.get('sources', None)

            return {
                'fulfillmentText': fulfillment_text,
                'sources': sources
            }

        except Exception as e:
            return {
                'fulfillmentText': f'An error occurred: {str(e)}',
                'sources': None
            }

def load_known_faces():
    try:
        with open('face_encodings.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return [], []
    except Exception as e:
        print(f"Error loading encodings: {e}")
        return [], []

def save_known_faces(encodings, usernames):
    with open('face_encodings.pkl', 'wb') as f:
        pickle.dump((encodings, usernames), f)

def auto_encode(face_dir='faces/', username=None):
    if not os.path.exists(face_dir):
        raise FileNotFoundError(f"The directory {face_dir} does not exist.")
    
    known_face_encodings = []
    known_usernames = []
    processed_images = 0
    failed_images = 0
    
    for image_name in os.listdir(face_dir):
        if image_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            image_path = os.path.join(face_dir, image_name)
            
            try:
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                
                if face_encodings:
                    known_face_encodings.append(face_encodings[0])
                    name = username if username else os.path.splitext(image_name)[0]
                    known_usernames.append(name)
                    processed_images += 1
                else:
                    print(f"No faces found in {image_name}. Skipping.")
                    failed_images += 1
            
            except Exception as e:
                print(f"Error processing {image_name}: {e}")
                failed_images += 1
    
    print(f"Total images processed: {processed_images}")
    print(f"Images failed to process: {failed_images}")
    
    if known_face_encodings:
        save_known_faces(known_face_encodings, known_usernames)
    
    return known_face_encodings, known_usernames
