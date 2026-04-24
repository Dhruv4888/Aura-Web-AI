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
        # Cleaning markers and symbols for faster processing
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        # Gender Correction
        text_lower = text.lower()
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text_lower = text_lower.replace(wrong, right)
        return text_lower

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        # Speed +10% kiya hai taaki teacher energetic lage aur jaldi khatam ho
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-2Hz")
        await communicate.save(filename)

    def speak(self, text):
        clean_text = self.clean_text_for_speech(text)
        filename = "aura_voice.mp3"
        try:
            # Sync wrapper for async voice gen
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            pass

    def ask_stream(self, query, history):
        # Strict Teacher Prompt with emphasis on Class 1-12 only
        base_prompt = """You are 'Gyan Setu', a warm and patient teacher for Class 1 to 12. 
        Rules:
        1. Only answer subjects related to school (Math, Science, History, etc.).
        2. If the question is outside (movies, gossip, etc.), politely say: 'Beta, main sirf aapke school subjects mein madad kar sakta hoon.'
        3. Keep the tone like a real teacher in a classroom.
        4. Use simple examples. If Hindi is used, respond in Hinglish/Hindi."""
        
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.6 # Lower temperature for faster, stable response
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Beta, connection mein thodi dikkat hai."

aura = AuraAssistant()
