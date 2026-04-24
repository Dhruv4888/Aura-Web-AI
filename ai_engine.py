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
        except:
            st.error("API Key error!")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        # Professional cleaning: Remove all special characters and formatting
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        # Remove LaTeX/Complex symbols that slow down TTS
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Professional Gender Correction
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice(self, text, filename):
        # Using professional voices
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        # Rate +12% for crisp and quick professional delivery
        communicate = edge_tts.Communicate(text, selected_voice, rate="+12%", pitch="-1Hz")
        await communicate.save(filename)

    def speak(self, text):
        clean_text = self.clean_text_for_speech(text)
        filename = "aura_voice.mp3"
        try:
            # Running as a background task for slight speed gain
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_voice(clean_text, filename))
            
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask_stream(self, query, history):
        # Professional Teacher Prompt (No 'Beta')
        base_prompt = """You are 'Gyan Setu', a professional and knowledgeable academic mentor.
        Rules:
        1. Provide deep, descriptive, and accurate explanations for school subjects (Class 1-12).
        2. Tone: Respectful, clear, and professional. Use 'Aap' instead of 'Tum'.
        3. Strictly avoid non-academic topics. If asked, respond: 'Main keval shaikshik vishayon (academic subjects) mein hi sahayata kar sakta hoon.'
        4. Do not use informal words like 'Beta' or 'Bachhe'. Maintain a mentor-student decorum."""
        
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.4 # More focused and faster generation
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, takniki samasya ke karan sampark toot gaya hai."

aura = AuraAssistant()
