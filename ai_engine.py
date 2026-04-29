import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64

class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        # API Key check
        if "GROQ_API_KEY" in st.secrets:
            self.api_key = st.secrets["GROQ_API_KEY"]
        else:
            self.api_key = os.environ.get("GROQ_API_KEY", "")
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    async def _generate_voice_bytes(self, text):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        if not text.strip(): return None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(text))
            return base64.b64encode(audio_raw).decode()
        except: return None

    def ask_stream(self, query, history):
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI (Devanagari script)" if is_hindi_in else "ENGLISH"
        system_instruction = f"You are 'Gyan Setu'. Respond strictly in {forced_lang}. Short sentences only. End with '.' or '।'."
        
        messages = [{"role": "system", "content": system_instruction}]
        for msg in history[-2:]: messages.append(msg)
        messages.append({"role": "user", "content": query})

        completion = self.client.chat.completions.create(
            messages=messages, model=self.model, stream=True, temperature=0.3
        )
        for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                yield content
                if any(mark in content for mark in ['.', '!', '?', '।', '\n']):
                    yield "||SYNC_SIGNAL||"

# CRITICAL: Ye line class ke bahar honi chahiye
aura = AuraAssistant()
