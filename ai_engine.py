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
            # Secrets se API Key access karna - High Priority
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"API Key Error: {e}")

    def is_hindi(self, text):
        # Hindi script (Devanagari) detect karne ka logic for accurate voice switching
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        # Audio generation se pehle text ki safai aur unnecessary symbols hatana
        # Isse voice generation mein koi "thud" ya ajeeb noise nahi aati
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Gender aur grammar corrections for natural AI persona
        corrections = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon"
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        """In-memory audio generation for zero-latency performance"""
        # Madhur for Hindi, Prabhat for English
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Rate +15% is tested for professional fast-paced learning
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """Sentence-level audio bytes generation with proper loop handling"""
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip():
            return None
            
        try:
            # Manage internal asyncio loop for Streamlit threads
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_bytes = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_bytes).decode()
        except Exception as e:
            st.error(f"TTS Engine Error: {e}")
            return None

    def ask_stream(self, query, history):
        # Logic to force language based on user's input script
        is_hindi_script = self.is_hindi(query)
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'samajh', 'sir']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        CORE OPERATING PROTOCOLS:
        1. Language: Strictly {forced_lang}.
        2. Format: Start directly. NEVER use "Aap," "Ji," or "Student,".
        3. Script: Use Devanagari for Hindi.
        4. Tone: Academic, professional, and precise.
        5. Punctuation: End every distinct thought with . or । immediately to trigger audio sync."""

        messages = [{"role": "system", "content": system_instruction}]
        # Using last 4 messages for deep context while maintaining speed
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Context: Student asks {query}. Reply directly in {forced_lang}."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Signal for UI to wait and play audio
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"System Error: {str(e)}"

# Global Access Point
aura = AuraAssistant()
