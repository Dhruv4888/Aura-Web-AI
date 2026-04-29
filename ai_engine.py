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
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"Boot Error: {e}")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        # Clean text for better pronunciation
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        gender_fix = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        # Language detection logic for correct voice selection
        is_h = self.is_hindi(text)
        selected_voice = "hi-IN-MadhurNeural" if is_h else "en-IN-PrabhatNeural"
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
        except:
            return None

    def ask_stream(self, query, history):
        is_hindi_in = self.is_hindi(query)
        
        # STRICT LANGUAGE PROTOCOL
        if is_hindi_in:
            lang_instruction = "Respond ONLY in Hindi script (Devanagari). Do not mix English words in between."
        else:
            lang_instruction = "Respond ONLY in English. Do not use Hindi words."

        system_instruction = f"""You are 'Gyan Setu'. {lang_instruction}
        1. Direct answers for Class 1-12.
        2. Maximum 3 short sentences.
        3. End every single sentence with a full stop (.) or (।)."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})

        try:
            completion = self.client.chat.completions.create(
                messages=messages, model=self.model, stream=True, temperature=0.3
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Rapid trigger for synchronization
                    if any(mark in content for mark in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
        except Exception as e:
            yield f"Error: {str(e)}"

aura = AuraAssistant()
