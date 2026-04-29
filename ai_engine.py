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
            # High Priority API Access
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            st.error(f"System Configuration Error: {e}")

    def is_hindi(self, text):
        # Accurate script detection for voice switching
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """Pre-processing text for a clean, natural vocal output without artifacts."""
        # Removing Wikipedia tags and markdown noise
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        
        # Math symbol conversion for natural speech
        text = text.replace("$", " dollar ")
        text = text.replace("^2", " squared ").replace("²", " squared ")
        text = text.replace("^3", " cubed ").replace("³", " cubed ")
        text = text.replace("+", " plus ").replace("-", " minus ").replace("=", " equals ")
        text = text.replace("#", "").replace("*", "").replace("`", "")
        
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Persona consistency: Keeping the 'Senior Academic Mentor' identity solid
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
        """RAM-based audio streaming to eliminate disk I/O lag."""
        # Madhur for Hindi context, Prabhat for English/Scientific context
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Professional pace (+15%) and steady pitch for authority
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """Generates base64 audio data with robust loop management for Streamlit threads."""
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip():
            return None
            
        try:
            # Handling asyncio loops within Streamlit's multi-threaded environment
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_bytes = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_bytes).decode()
        except Exception as e:
            print(f"Vocal Engine Processing Error: {e}")
            return None

    def ask_stream(self, query, history):
        """Streams AI responses with intelligent break-points for smooth vocal synchronization."""
        is_hindi_script = self.is_hindi(query)
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'samajh', 'formula']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        # Strict instructions for mathematical clarity and prefix-free output
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        PROTOCOL RULES:
        1. Response Language: Strictly {forced_lang}.
        2. Directness: Start directly with the core solution. NEVER use "Student," "Ji," or "Aap," as prefixes.
        3. Math/Science: Explain step-by-step. Use standard punctuation (. or ।) after each step.
        4. Tone: Academic, helpful, and highly professional.
        5. Output Script: Use Devanagari for Hindi; strictly avoid Romanized Hindi."""

        messages = [{"role": "system", "content": system_instruction}]
        # Maintaining 4-turn memory for deep context
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Academic Inquiry: {query}. Respond in {forced_lang}."})
        
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
                    # SYNC TRIGGER: Breaks on punctuation OR newline (crucial for math equations)
                    # This ensures the voice engine doesn't get overwhelmed by long text blocks
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Computational Error: {str(e)}"

# Global Assistant Instance
aura = AuraAssistant()
