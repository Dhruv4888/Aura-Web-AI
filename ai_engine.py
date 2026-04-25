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
        # Improved Hindi detection
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        return text

    async def _generate_voice(self, text, filename):
        # Awaaz select hogi response ki script dekh kar
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
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
        # HARD LANGUAGE DETECTION
        is_hindi_query = self.is_hindi(query)
        target_lang = "HINDI (Devanagari script)" if is_hindi_query else "ENGLISH"
        
        # Professional Teacher Prompt
        system_prompt = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT RULES:
        1. IF user speaks Hindi, YOU MUST reply 100% in Hindi script.
        2. IF user speaks English, YOU MUST reply 100% in English.
        3. NO MIXING. NO HINGLISH.
        4. Tone: Academic, professional, use 'Aap'.
        5. Current target language: {target_lang}."""

        # Context filter: Only last 2 messages to avoid language confusion
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-2:]) 
        messages.append({"role": "user", "content": f"Answer strictly in {target_lang}: {query}"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1, # Zero randomness
                top_p=0.1
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
