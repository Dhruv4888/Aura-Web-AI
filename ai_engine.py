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
        Gyan Setu Core Engine - 100% Streaming Optimized.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("GROQ_API_KEY not found.")
        except Exception as e:
            st.error(f"Boot Error: {e}")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        Phonetic cleaning optimized for streaming chunks.
        """
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        
        # Senior Mentor Gender Correction
        gender_fix = {
            "sakti hoon": "sakta hoon", "karti hoon": "karta hoon",
            "rahi hoon": "raha hoon", "huu": "hoon"
        }
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        """
        Fast TTS synthesis for individual sentence chunks.
        """
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+12%", pitch="-2Hz")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """
        Converts the streamed sentence into voice data immediately.
        """
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip(): return None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_raw).decode()
        except Exception:
            return None

    def ask_stream(self, query, history):
        """
        100% TEXT STREAMING ENGINE.
        Yields character-by-character for the UI and sends a SYNC signal at sentence ends.
        """
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI" if (is_hindi_in or " btao" in query.lower()) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu'. Respond strictly in {forced_lang}.
        1. Give direct answers for Class 1-12. 
        2. Use 3-4 clear sentences.
        3. End each sentence with a full stop (.) or (।)."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})

        try:
            # Groq implementation for raw text streaming
            completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                stream=True,
                temperature=0.2,
                max_tokens=400
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    # yield the raw text for UI streaming
                    yield content
                    
                    # TRIGGER: Sentence completion detection for TTS sync
                    if any(mark in content for mark in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"

        except Exception as e:
            yield f"Error: {str(e)}"

aura = AuraAssistant()
