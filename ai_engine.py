import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st

class AuraAssistant:
    def __init__(self):
        try:
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except:
            st.error("API Key missing in Secrets!")
            
        self.model = "llama-3.3-70b-versatile"

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(filename)

    def speak(self, text):
        clean_text = text.replace("*", "").replace("#", "")
        filename = "speech.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            st.error(f"Voice Error: {e}")

    def ask(self, query):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are Aura, a professional AI. Reply concisely."},
                    {"role": "user", "content": query}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except:
            return "Connection error, Sir."

aura = AuraAssistant()
