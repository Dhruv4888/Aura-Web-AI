import os
import asyncio
import edge_tts
from groq import Groq
import re
import time
import streamlit as st # Zaroori link ke liye

class AuraAssistant:
    def __init__(self):
        # Option 2: Secrets se key uthana
        try:
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"Setup Error: API Key missing in Secrets!")
            
        self.model = "llama-3.3-70b-versatile"
        self.recognizer = sr.Recognizer()

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.pause_threshold = 0.8
            try:
                audio = self.recognizer.listen(source, timeout=5)
                query = self.recognizer.recognize_google(audio, language='en-in')
                return query.lower()
            except:
                return ""

    async def _generate_voice(self, text, filename):
        if self.is_hindi(text):
            selected_voice = "hi-IN-MadhurNeural"
        else:
            selected_voice = "en-IN-PrabhatNeural"
        
        communicate = edge_tts.Communicate(text, selected_voice)
        await communicate.save(filename)

    def speak(self, text):
        clean_text = text.replace("*", "").replace("#", "")
        filename = "speech.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            # Browser mein audio play karne ke liye Streamlit ka use
            with open(filename, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            st.warning(f"Voice output error: {e}")

    def ask(self, query):
        if not query: return ""
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
            return "Sir, connection error."

aura = AuraAssistant()
