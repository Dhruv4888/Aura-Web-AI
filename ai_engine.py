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
        except Exception as e:
            st.error(f"API Key Error: {e}")

    def is_hindi(self, text):
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
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        await communicate.save(filename)

    def get_audio_data(self, text):
        clean_text = self.clean_text_for_speech(text)
        filename = f"temp_{hash(clean_text)}.mp3"
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_voice(clean_text, filename))
            
            import base64
            with open(filename, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            
            if os.path.exists(filename):
                os.remove(filename)
            return data
        except Exception as e:
            return None

    def ask_stream(self, query, history):
        is_hindi_script = self.is_hindi(query)
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        RULES:
        1. Respond strictly in {forced_lang}.
        2. Use Devanagari script for Hindi.
        3. Keep sentences clear and professional. Use 'Aap'.
        4. End sentences with punctuation like . or । immediately."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": f"Question: {query}\n\nReply in {forced_lang}."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.0
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Error in processing: {str(e)}"

# Yahan se 'from ai_engine import aura' wali line hata di hai jo error de rahi thi
aura = AuraAssistant()
