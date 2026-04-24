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
        # Cleaning for smooth professional voice delivery
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Professional Gender Correction
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        # Rate set to +10% for a natural yet professional flow
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-1Hz")
        await communicate.save(filename)

    def speak(self, text):
        clean_text = self.clean_text_for_speech(text)
        filename = "aura_voice.mp3"
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_voice(clean_text, filename))
            
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask_stream(self, query, history):
        # BALANCED PROMPT: Descriptive but structured for speed
        base_prompt = """You are 'Gyan Setu', a highly professional academic mentor for Class 1-12.
        Rules:
        1. Provide descriptive and detailed explanations for academic subjects.
        2. Format the answer using bullet points and clear headings to make it structured.
        3. Avoid unnecessary filler words to keep the voice generation efficient.
        4. Tone: Academic, respectful, and formal (Use 'Aap'). No 'Beta' or 'Bachhe'.
        5. If a topic is very large, explain the most important 4-5 points in detail.
        6. Strictly refuse non-academic queries politely."""
        
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.5, 
                max_tokens=700    # Increased limit for "Detail" while keeping it safe for TTS
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
