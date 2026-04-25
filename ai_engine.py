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
        # Detecting Devanagari script for strict language locking
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice(self, text, filename):
        # Voice selection based on actual content of the generated text
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+12%", pitch="-1Hz")
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
        # Determine strict language lock
        is_hindi_input = self.is_hindi(query)
        forced_lang = "HINDI (Devanagari)" if is_hindi_input else "ENGLISH"
        
        # Professional Teacher System Instructions
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT RULES:
        1. Current Language: {forced_lang}. You MUST speak 100% in {forced_lang}.
        2. Tone: Professional, respectful (Use 'Aap'). No 'Hello/Hi' in mixed languages.
        3. Structure: Use bullet points and clear headings.
        4. Focus: Strictly academic. 
        5. If input is Hindi characters, reply in Hindi script ONLY. If English, reply in English ONLY."""
        
        # Crafting messages to prevent drift
        messages = history[-2:] # Only keep very recent context to avoid language confusion
        messages.insert(0, {"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": f"Query: {query}\nTeacher, please answer this strictly in {forced_lang}."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1, # Lowest possible for strict adherence
                top_p=0.9
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
