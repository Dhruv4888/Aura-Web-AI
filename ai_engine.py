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
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-2Hz")
        await communicate.save(filename)

    def speak(self, text):
        # Strict Gender Correction
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        clean_text = text.lower()
        for wrong, right in corrections.items():
            clean_text = clean_text.replace(wrong, right)
        
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask(self, query, history):
        try:
            # Professional System Prompt
            messages = [{"role": "system", "content": "You are AURA, a highly professional MALE AI. Maintain context from previous chats. Use formal Hindi/English. Gender: Male. No fluff, direct answers."}]
            messages.extend(history)
            messages.append({"role": "user", "content": query})

            chat_completion = self.client.chat.completions.create(messages=messages, model=self.model)
            return chat_completion.choices[0].message.content
        except:
            return "Connection lost, Sir."

aura = AuraAssistant()
