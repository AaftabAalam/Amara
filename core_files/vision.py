# import asyncio
# from typing import Annotated
# from dotenv import load_dotenv
# import os
# from livekit import agents, rtc
# from livekit.agents import JobContext, WorkerOptions, cli, tokenize, tts
# from livekit.agents.llm import ChatContext, ChatImage, ChatMessage
# from livekit.agents.voice_assistant import VoiceAssistant
# from livekit.plugins import deepgram, silero, openai
# from deepgram import Deepgram
# import argparse

# load_dotenv()

# livekit_url = os.getenv("LIVEKIT_URL")
# livekit_api_key = os.getenv("LIVEKIT_API_KEY")
# livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
# deepgram_api_key = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
# groq_api_key = os.getenv("GROQ_API_KEY")
# openai_api_key = os.getenv("OPENAI_API_KEY")

# class AssistantFunction(agents.llm.FunctionContext):
#     """This class is used to define functions that will be called by the assistant."""

#     @agents.llm.ai_callable(
#         description=(
#             "Called when asked to evaluate something that would require vision capabilities,"
#             " for example, analyze image, video, or the webcam and give feedback."
#         )
#     )
#     async def image(self, user_msg: Annotated[str, agents.llm.TypeInfo(description="The user message that triggered this function")]):
#         print(f"Message triggering vision capabilities: {user_msg}")
#         return await self.analyze_appearance(user_msg)
    
#     async def analyze_appearance(self, user_msg: str):

#         if 'hello' in user_msg.lower():
#             return "Hello there! You look great today."
#         elif 'how do I look' in user_msg.lower():
#             return "You look fantastic! Keep up the good work."
#         else:
#             return "Nice to see you! How can I assist you today?"

# async def get_video_track(room: rtc.Room):
#     """Get the first video track from the room. We'll use this track to process images."""
#     video_track = asyncio.Future[rtc.RemoteVideoTrack]()
#     for _, participant in room.remote_participants.items():
#         for _, track_publication in participant.track_publications.items():
#             if track_publication.track is not None and isinstance(track_publication.track, rtc.RemoteVideoTrack):
#                 video_track.set_result(track_publication.track)
#                 print(f"Using video track {track_publication.track.sid}")
#                 break
#     return await video_track

# async def entrypoint(ctx: JobContext):
#     await ctx.connect()
#     print(f"Room name: {ctx.room.name}")

#     chat_context = ChatContext(
#         messages=[
#             ChatMessage(
#                 role="system",
#                 content=(
#                     "Your name is metal. First make greetings and detect users surroundings and comment on them before user say anything. Your work is to first of all say greetings and comment them on their cloths, appearance and surroundings."
#                     "Do not say i can't see you, you have function to analyze video so check their appearance and greet them accordingly with their surroundings where they present."
#                     "Then ask them about their day. Keep your answers concise."
#                 ),
#             )
#         ]
#     )
#     gpt = openai.LLM(model="gpt-4o")

#     openai_tts = tts.StreamAdapter(
#         tts = openai.TTS(voice='alloy'),
#         sentence_tokenizer = tokenize.basic.SentenceTokenizer()
#     )
#     latest_image: rtc.VideoFrame | None = None

#     assistant = VoiceAssistant(
#         vad=silero.VAD.load(),
#         stt=deepgram.STT(), 
#         llm=gpt,
#         tts=openai_tts,
#         fnc_ctx=AssistantFunction(),
#         chat_ctx=chat_context,
#     )

#     chat = rtc.ChatManager(ctx.room)

#     async def _answer(text: str, use_image: bool = False):
#         """
#         Answer the user's message with the given text and optionally the latest
#         image captured from the video track.
#         """
#         content: list[str | ChatImage] = [text]
#         if use_image and latest_image:
#             content.append(ChatImage(image=latest_image))

#         chat_context.messages.append(ChatMessage(role="user", content=content))

#         stream = gpt.chat(chat_ctx=chat_context)
#         await assistant.say(stream, allow_interruptions=True)

#     @chat.on("message_received")
#     def on_message_received(msg: rtc.ChatMessage):
#         """This event triggers whenever we get a new message from the user."""
#         if msg.message:
#             asyncio.create_task(_answer(msg.message, use_image=False))

#     @assistant.on("function_calls_finished")
#     def on_function_calls_finished(called_functions: list[agents.llm.CalledFunction]):
#         """This event triggers when an assistant's function call completes."""

#         if len(called_functions) == 0:
#             return

#         user_msg = called_functions[0].call_info.arguments.get("user_msg")
#         if user_msg:
#             asyncio.create_task(_answer(user_msg, use_image=True))

#     assistant.start(ctx.room)

#     await asyncio.sleep(1)
#     await assistant.say("Hi there! How can I help?", allow_interruptions=True)

#     while ctx.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
#         video_track = await get_video_track(ctx.room)
#         async for event in rtc.VideoStream(video_track):
#             latest_image = event.frame

# def start_vision_assistant(mode):
#     if mode == 'dev':
#         print('starting vision assistant in development mode.')
#     elif mode == 'start':
#         print('starting vision assistant in production mode.')
#     else:
#         raise ValueError('Use dev or start mode to start the app')
#     cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Run the vision assistant')
#     parser.add_argument(
#         'mode',
#         choices=['start','dev'],
#         help='mode to run the vision assistant: dev or start'
#     )
#     args = parser.parse_args()
#     start_vision_assistant(args.mode)