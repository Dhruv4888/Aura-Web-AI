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
            # High Priority API Access from Streamlit Secrets
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"System Configuration Error: {e}")

    def is_hindi(self, text):
        # Accurate Devanagari script detection
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """Mathematical character expansion for clear vocalization."""
        # Removing Wikipedia tags and markdown artifacts
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        
        # Expanding symbols to words so the voice engine takes proper time to speak them
        text = text.replace("$", " dollar ")
        text = text.replace("^2", " squared ").replace("²", " squared ")
        text = text.replace("^3", " cubed ").replace("³", " cubed ")
        text = text.replace("+", " plus ").replace("-", " minus ").replace("=", " equals ")
        text = text.replace("x", " x ").replace("*", " multiplied by ")
        text = text.replace("/", " divided by ")
        text = text.replace("#", "").replace("`", "")
        
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Gender consistency for the 'Senior Academic Mentor' persona
        corrections = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon "
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice_bytes(self, text):
        """Generates audio bytes directly in RAM for maximum speed."""
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Professional pace with authoritative pitch
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """Converts text to base64 audio with safe asyncio loop management."""
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip():
            return None
            
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_bytes = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_bytes).decode()
        except Exception:
            return None

    def ask_stream(self, query, history):
        """Streams AI responses with aggressive break-points for mathematical equations."""
        is_hindi_script = self.is_hindi(query)
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'formula', 'equation']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        CORE PROTOCOLS:
        1. Language: Strictly {forced_lang}.
        2. Format: Start directly. NEVER use greetings or prefixes like "Aap" or "Student".
        3. Math/Science: Explain step-by-step. Break equations into small parts.
        4. Punctuation: Use . or । after every number or symbol group to force a vocal pause.
        5. Tone: Academic and highly professional."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Inquiry: {query}. Respond in {forced_lang}."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, model=self.model, stream=True, temperature=0.1
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Breaking on more signals to ensure smaller audio chunks (prevents overlap)
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n', ':', ';', '=']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Computational Error: {str(e)}"

aura = AuraAssistant()
