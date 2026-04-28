import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64
import io

class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        try:
            # Secrets se API Key access karna
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"API Key Error: {e}")

    def is_hindi(self, text):
        # Hindi script (Devanagari) detect karne ka logic
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        # Audio generation se pehle text ki safai aur symbols hatana
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Persona consistency ke liye gender corrections
        corrections = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon"
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        """File write karne ke bajaye memory mein bytes generate karta hai (Fast)"""
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """MP3 generate karke use base64 string mein badalta hai bina lag ke"""
        clean_text = self.clean_text_for_speech(text)
        try:
            # Naya loop banane ke bajaye existing loop handling
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_bytes = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_bytes).decode()
        except Exception as e:
            print(f"TTS Optimization Error: {e}")
            return None

    def ask_stream(self, query, history):
        # Language determine karna based on script and keywords
        is_hindi_script = self.is_hindi(query)
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'samajh']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT RULES:
        1. Respond strictly in {forced_lang}.
        2. Start directly with the answer. Do NOT use prefixes like "Aap" or "Greeting".
        3. Use Devanagari script for Hindi responses.
        4. TONE: Professional, precise, and academic.
        5. Structure: Use short, clear sentences. End each with . or । immediately."""

        messages = [{"role": "system", "content": system_instruction}]
        # History context length manage karna
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Question: {query}\n\nReply in {forced_lang} directly."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1 # Thoda sa temperature for natural flow
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Sentence break trigger for high-speed UI sync
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Error in processing: {str(e)}"

# Global instance
aura = AuraAssistant()
