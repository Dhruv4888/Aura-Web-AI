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
        # Strict detection for Devanagari (Hindi) script
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        # Removing formatting symbols for cleaner voice synthesis
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Gender corrections for a male teacher persona
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice(self, text, filename):
        # Selecting voice based on the actual text content generated
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
        # STEP 1: Determine Language Lock
        is_hindi_input = self.is_hindi(query)
        forced_lang = "HINDI (Devanagari Script)" if is_hindi_input else "ENGLISH"
        
        # STEP 2: Strict Professional Teacher System Prompt
        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor and Teacher.
        STRICT OPERATING RULES:
        1. LANGUAGE: Respond 100% in {forced_lang} ONLY. 
        2. IF User speaks Hindi, use ONLY Hindi script (Devanagari). No English words.
        3. IF User speaks English, use ONLY English. No Hindi words.
        4. TONE: Professional, formal, and academic. Use 'Aap' to address students.
        5. FORMAT: Use bullet points for clear explanations.
        6. NO GREETINGS: Do not use mixed language greetings like 'Namaste, how can I help'."""

        # STEP 3: Message Construction (Bypassing history confusion)
        messages = [{"role": "system", "content": system_instruction}]
        
        # Add a very limited history (last 2) to maintain context but avoid language drift
        messages.extend(history[-2:])
        
        # Final forceful user prompt
        messages.append({"role": "user", "content": f"Student Question: {query}\n(Teacher, answer this strictly in {forced_lang} only)"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1, # Extremely low for strict adherence
                top_p=0.1        # Focused output
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
