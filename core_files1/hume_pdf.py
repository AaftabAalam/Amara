import os
import asyncio
import pdfplumber
from hume import AsyncHumeClient
from hume.expression_measurement.stream import Config
from hume.expression_measurement.stream.socket_client import StreamConnectOptions
from hume.expression_measurement.stream.types import StreamLanguage
from dotenv import load_dotenv

load_dotenv()


async def analyze_text(text):
    client = AsyncHumeClient(api_key=os.getenv("HUME_API_KEY"))
    model_config = Config(language=StreamLanguage())
    stream_options = StreamConnectOptions(config=model_config)

    async with client.expression_measurement.stream.connect(options=stream_options) as socket:
        result = await socket.send_text(text)
        emotions = result.language.predictions[0].emotions
        return {emotion.name: round(emotion.score, 4) for emotion in emotions}

def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text

