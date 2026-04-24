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

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+5%", pitch="-2Hz")
        await communicate.save(filename)

    def speak(self, text):
        clean_text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        clean_text = clean_text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        
        # Gender Correction
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        clean_text = clean_text.lower()
        for wrong, right in corrections.items():
            clean_text = clean_text.replace(wrong, right)
        
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask_stream(self, query, history):
        # (Same System Prompt)
        base_prompt = """You are Gyan Setu — a warm, patient teacher... (rules 1-10)"""
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        try:
            completion = self.client.chat.completions.create(messages=messages, model=self.model, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except: yield "Connection lost, Sir."

aura = AuraAssistant()
