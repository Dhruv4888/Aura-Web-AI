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
        # Strict detection for Devanagari script
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
        # Awaaz select hogi response ki script dekh kar
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
        # --- NEW DEEP DETECTION LOGIC ---
        is_hindi_script = self.is_hindi(query)
        # Roman Hindi keywords to force Hindi mode
        roman_hindi_words = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kise', 'kyun', 'kya hai']
        is_roman_hindi = any(word in query.lower() for word in roman_hindi_words)
        
        # Decide Language
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        # Super Strict Teacher Prompt
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT OPERATING RULES:
        1. LANGUAGE: Respond 100% in {forced_lang} ONLY. 
        2. NO HINGLISH: If the language is HINDI, use ONLY Devanagari script. No English alphabets.
        3. TONE: Professional, formal, use 'Aap'.
        4. FORMAT: Use bullet points. No unnecessary greetings."""

        messages = [{"role": "system", "content": system_instruction}]
        
        # Keeping history minimal to avoid drift
        messages.extend(history[-2:])
        
        # The "Hard-Lock" instruction to the model
        messages.append({"role": "user", "content": f"Student Question: {query}\n\n(Note: Reply strictly and entirely in {forced_lang}. First word must be in {forced_lang}.)"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.0, # Zero for maximum rule following
                top_p=0.1
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
