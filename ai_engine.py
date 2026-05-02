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
        Gyan Setu Core Engine - Async V14.
        Optimized for Parallel Text-to-Voice Synchronization.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("System Error: GROQ_API_KEY is not defined.")
        except Exception as e:
            st.error(f"Critical Boot Failure: {e}")

    def is_hindi(self, text):
        if not text: return False
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """Phonetic Re-engineering for Academic Excellence."""
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        
        # Fast Math Mapping
        math_map = {"²": " square", "^2": " square", " + ": " plus ", " = ": " equals to ", " / ": " divided by "}
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)
        
        # Persona Logic
        gender_fix = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
        return text

    async def generate_voice_async(self, text):
        """Background Audio Generation - Non-blocking."""
        if not text.strip(): return None
        clean_text = self.clean_text_for_speech(text)
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(clean_text) else "en-IN-PrabhatNeural"
        
        try:
            communicate = edge_tts.Communicate(clean_text, selected_voice, rate="+10%", pitch="-2Hz")
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return base64.b64encode(audio_data).decode()
        except:
            return None

    async def ask_stream(self, query, history):
        """
        Async Streamer: Yields characters and sync signals without blocking the loop.
        """
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI (Strictly Devanagari)" if is_hindi_in else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor.
        1. LANGUAGE: {forced_lang}. 
        2. CONTENT: Concise academic solution (3-5 sentences).
        3. SYNC: Finish every logical sentence with a period (.) or (।).
        4. PERSONA: Male Teacher, authoritative."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})

        try:
            # Groq Stream - Calling via thread to keep it async friendly
            completion = await asyncio.to_thread(
                self.client.chat.completions.create,
                messages=messages, 
                model=self.model, 
                stream=True, 
                temperature=0.1, 
                max_tokens=450
            )

            for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    for char in token:
                        yield char
                        # Smooth typing speed
                        await asyncio.sleep(0.01)

                    if any(p in token for p in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Error: {str(e)}"

# Global instance
aura = AuraAssistant()
