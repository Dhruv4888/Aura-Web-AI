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
        """
        Initializing the Academic Mentor Engine. 
        Focus: Precision, Speed, and Zero-Lag Synchronization.
        """
        self.model = "llama-3.3-70b-versatile"
        # API Key Retrieval with Multiple Fallbacks
        self.api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            st.error("Engine Failure: GROQ_API_KEY not found. Please check secrets.")

    def is_hindi(self, text):
        """Detects if the input context is Hindi to toggle the correct Vocal Engine."""
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        Sanitizes text for 'Madhur' and 'Prabhat' voices.
        Fixes gender issues and removes non-verbal characters.
        """
        # Remove markdown and wiki-search tags
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        
        # Masculine Tone Correction (Student Mentor Profile)
        gender_map = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "hoon main ek assistant": "hoon main aapka mentor"
        }
        for wrong, right in gender_map.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        """
        Low-level async call to Edge-TTS. 
        Calibrated for +15% rate to match human reading speed.
        """
        clean_text = self.clean_text_for_speech(text)
        is_h = self.is_hindi(clean_text)
        
        # Voice Selection: Madhur (Hindi) | Prabhat (English-India)
        selected_voice = "hi-IN-MadhurNeural" if is_h else "en-IN-PrabhatNeural"
        
        communicate = edge_tts.Communicate(
            clean_text, 
            selected_voice, 
            rate="+18%", 
            pitch="-1Hz"
        )
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """Bridge between Streamlit's Sync Loop and TTS's Async Loop."""
        if not text.strip() or len(text.strip()) < 2:
            return None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(text))
            return base64.b64encode(audio_raw).decode()
        except Exception as e:
            print(f"Vocal Sync Error: {e}")
            return None

    def ask_stream(self, query, history):
        """
        Main Academic Streamer.
        Logic: Detects language -> Sets Persona -> Streams with Sync Markers.
        """
        is_hindi_query = self.is_hindi(query)
        
        # STRICT LANGUAGE PROTOCOL: Prevents 'Hinglish' mix-up for cleaner speech.
        if is_hindi_query:
            lang_instruction = "Respond ONLY in Hindi (Devanagari script). No English alphabets allowed."
        else:
            lang_instruction = "Respond ONLY in English. Do not use any Hindi words."

        system_instruction = f"""
        You are 'Gyan Setu', a high-authority Academic Mentor for students (Class 1-12).
        Instruction: {lang_instruction}
        Style: Professional, encouraging, and very concise.
        Constraint: Maximum 2-3 short sentences. 
        CRITICAL: You MUST end every sentence with a full stop (.) or Purna Viram (।).
        """

        messages = [{"role": "system", "content": system_instruction}]
        # Context management: Last 4 turns for deeper understanding
        for msg in history[-4:]:
            messages.append(msg)
        messages.append({"role": "user", "content": query})

        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model, 
                stream=True, 
                temperature=0.4 # Balanced creativity and accuracy
            )

            for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    yield token
                    # SYNC TRIGGER: Whenever a sentence completes, we signal the UI to fetch audio.
                    if any(punc in token for punc in ['.', '!', '?', '।', '\n']):
                        yield "||SENTENCE_COMPLETE_SIGNAL||"
        
        except Exception as e:
            yield f"Engine Error: {str(e)}"

# Instantiate the global assistant object
aura = AuraAssistant()
