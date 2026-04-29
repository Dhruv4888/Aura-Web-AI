import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64
import time

class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        if "GROQ_API_KEY" in st.secrets:
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        # Gender Correction
        gender_fix = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip(): return None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_raw).decode()
        except: return None

    def ask_stream(self, query, history):
        # Language Protocol based on query
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI (Devanagari script)" if is_hindi_in else "ENGLISH"
        
        system_instruction = f"You are 'Gyan Setu'. Respond strictly in {forced_lang}. Use short sentences. End with '.' or '।'."
        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
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
