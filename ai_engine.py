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
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception:
            st.error("Missing API Key!")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    async def _generate_voice(self, text, filename):
        if self.is_hindi(text):
            selected_voice = "hi-IN-MadhurNeural"
        else:
            selected_voice = "en-IN-PrabhatNeural"
        
        # Rate thoda fast taaki natural lage
        communicate = edge_tts.Communicate(text, selected_voice, rate="+12%", pitch="-1Hz")
        await communicate.save(filename)

    def speak(self, text):
        # Gender Correction Logic: Agar AI galti se "sakti" bole toh usse "sakta" kar do
        clean_text = text.replace("sakti hoon", "sakta hoon").replace("karti hoon", "karta hoon")
        clean_text = clean_text.replace("Rahi hoon", "Raha hoon").replace("*", "").replace("#", "")
        
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            st.error(f"Voice Error: {e}")

    def ask(self, query):
        if not query: return ""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Aura, a professional MALE AI assistant. Always use male gender terms in Hindi (like 'karta hoon', 'sakta hoon'). Keep your responses short and smart."
                    },
                    {"role": "user", "content": query}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except:
            return "Connection error, Sir."

aura = AuraAssistant()
