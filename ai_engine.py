import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64

class AuraAssistant:
    def __init__(self):
        """
        Gyan Setu Core Engine - V15 (The Final Sync).
        Focus: Precise Audio Duration Tracking to eliminate Overlap.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("Critical: API Key missing.")
        except Exception as e:
            st.error(f"Boot Failure: {e}")

    def is_hindi(self, text):
        if not text: return False
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        math_map = {"²": " square", "^2": " square", " + ": " plus ", " = ": " equals to ", " / ": " divided by "}
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)
        
        gender_fix = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
        return text

    async def generate_voice_async(self, text):
        """
        Generates audio AND returns duration to prevent overlapping.
        """
        if not text.strip(): return None, 0
        clean_text = self.clean_text_for_speech(text)
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(clean_text) else "en-IN-PrabhatNeural"
        
        try:
            communicate = edge_tts.Communicate(clean_text, selected_voice, rate="+15%", pitch="-2Hz")
            audio_data = b""
            
            # Edge-TTS duration estimation (Chars per second approx)
            # Standard Madhur/Prabhat +15% rate is roughly 14-16 chars per second
            char_count = len(clean_text)
            estimated_duration = (char_count / 14.5) + 0.3 # Buffer for natural pause
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            b64_audio = base64.b64encode(audio_data).decode()
            return b64_audio, estimated_duration
        except:
            return None, 0

    async def ask_stream(self, query, history):
        """
        High-Speed Async Generator for Real-time Text & Sync Triggers.
        """
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI (Strictly Devanagari)" if is_hindi_in else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor.
        1. LANGUAGE: {forced_lang}. 
        2. CONTENT: Concise academic solution (Max 4 sentences).
        3. SYNC: Finish every sentence with a period (.) or (।).
        4. PERSONA: Male Teacher, authoritative."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})

        try:
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                messages=messages, model=self.model, stream=True, temperature=0.1
            )

            for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    for char in token:
                        yield char
                        await asyncio.sleep(0.005) # Targeted Typing Speed

                    if any(p in token for p in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Engine Error: {str(e)}"

aura = AuraAssistant()
