import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st

class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        try:
            # Sahi Secret Handling
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error("Missing GROQ_API_KEY in Streamlit Secrets!")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    async def _generate_voice(self, text, filename):
        # Voice selection logic restore kiya
        if self.is_hindi(text):
            selected_voice = "hi-IN-MadhurNeural"
        else:
            selected_voice = "en-IN-PrabhatNeural"
        
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(filename)

    def speak(self, text):
        # Text cleaning restore kiya
        clean_text = text.replace("*", "").replace("#", "")
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            # Browser Autoplay feature
            with open(filename, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            
            # Temporary file cleanup
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            st.error(f"Voice System Error: {e}")

    def ask(self, query):
        if not query: return ""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are Aura, a professional AI assistant. Keep responses smart and concise."},
                    {"role": "user", "content": query}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception:
            return "Sir, I'm having trouble connecting to my brain. Please check your internet."

# Assistant instance for the Web UI
aura = AuraAssistant()
