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
        # Professional cleaning for faster TTS processing
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
        # Rate +12% for professional and crisp delivery
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
        # NEW: Optimized Prompt for Short & Professional Responses
        base_prompt = """You are 'Gyan Setu', a professional academic mentor.
        Rules:
        1. Answer ONLY school subjects (Class 1-12).
        2. VERY IMPORTANT: Keep answers concise, clear, and to-the-point. No long essays.
        3. Explain complex topics in maximum 2-3 short paragraphs or bullet points.
        4. Tone: Professional and respectful (Use 'Aap'). 
        5. Strictly avoid informal words like 'Beta' or 'Bachhe'.
        6. If asked outside academics, say: 'Main keval shaikshik vishayon mein hi sahayata kar sakta hoon.'"""
        
        messages = [{"role": "system", "content": base_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.3, # Focused and fast
                max_tokens=350    # Short response limit for ultra-fast voice generation
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
