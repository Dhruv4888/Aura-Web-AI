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
        """
        Gyan Setu Global Mentor Engine Initialization.
        This core is designed to handle Class 1 to 12 academic curricula 
        across Mathematics, Sciences, and Social Studies.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            # High-priority check for the API infrastructure
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("Engine Authentication Failure: GROQ_API_KEY not found in secrets.")
        except Exception as e:
            st.error(f"Critical System Boot Error: {e}")

    def is_hindi(self, text):
        """
        Advanced Linguistic Detection.
        Identifies Devanagari script to trigger the correct phonetic engine.
        """
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        DEEP PHONETIC RE-ENGINEERING (NON-SHORTCUT VERSION):
        This section ensures that complex math, physics formulas, and history 
        narratives are spoken with perfect academic clarity.
        """
        # Step 1: Cleaning Technical Markdown & Metadata
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Step 2: High-Resolution Mathematical & Scientific Mapping
        # We use explicit spacing and commas to force the TTS to create 'vocal gaps'.
        academic_phonetic_map = {
            "²": " square, ",
            "^2": " square, ",
            "³": " cube, ",
            "^3": " cube, ",
            "x²": " x square, ",
            " + ": " plus ",
            " - ": " minus ",
            " = ": " equals to ",
            " / ": " divided by ",
            " * ": " multiplied by ",
            " x ": " x ", # Keep it natural for '2 x'
            "2x": " 2 x ", 
            "3x": " 3 x ",
            "4x": " 4 x ",
            "5x": " 5 x ",
            "√": " square root of ",
            "π": " pi ",
            "(": " bracket start, ",
            ")": " bracket close, ",
            "H2O": " H, 2, O ", # Chemistry support
            "CO2": " C, O, 2 "
        }
        
        # Deep cleaning: Iterative replacement to ensure no symbols are missed
        for symbol, phonetic_word in academic_phonetic_map.items():
            text = text.replace(symbol, phonetic_word)

        # Step 3: Global Gender & Persona Alignment (Male Senior Mentor)
        # Ensuring grammar is consistently masculine as per Gyan Setu's identity.
        persona_normalization = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ",
            "main ek machine hoon": "Main aapka mentor, Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon, aapka shikshak"
        }
        
        for error, correction in persona_normalization.items():
            text = text.replace(error, correction)
            
        return text

    async def _generate_voice_bytes(self, text):
        """
        Real-time Vocal Synthesis with Rate Modulation.
        Rate is set to +8% to ensure complex definitions are understandable.
        """
        # Selecting the appropriate neural voice for the detected language
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Tone: Professional, Pitch: Authoritative (-2Hz), Rate: Academic (+8%)
        communicate = edge_tts.Communicate(text, selected_voice, rate="+8%", pitch="-2Hz")
        
        audio_buffer = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer += chunk["data"]
        return audio_buffer

    def get_audio_data(self, text):
        """
        Thread-safe Interface for Streamlit integration.
        Manages asynchronous loops for synchronous UI delivery.
        """
        cleaned_payload = self.clean_text_for_speech(text)
        if not cleaned_payload.strip():
            return None
            
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(cleaned_payload))
            return base64.b64encode(audio_raw).decode()
        except Exception as tts_err:
            print(f"Vocal Synthesis Error: {tts_err}")
            return None

    def ask_stream(self, query, history):
        """
        The Reasoning & Language Processing Core.
        Ensures History, Science, and Math are all delivered in the user's preferred tongue.
        """
        # Multi-subject Language Detection
        is_hindi_input = self.is_hindi(query)
        # Expanding keywords to capture social science and general science queries in Hinglish
        hinglish_markers = ['kya', 'tha', 'kaun', 'kab', 'kyun', 'kaise', 'batao', 'samjhao', 'uddeshya', 'vistar', 'likho']
        is_roman_hindi = any(marker in query.lower() for marker in hinglish_markers)
        
        assigned_lang = "HINDI (Devanagari Script)" if (is_hindi_input or is_roman_hindi) else "ENGLISH"
        
        # SYSTEM PROTOCOL - DEFINING THE ACADEMIC MENTOR BEHAVIOR
        system_protocol = f"""You are 'Gyan Setu', a formal Senior Academic Mentor for Classes 1 to 12.
        
        SUBJECT EXPERTISE: Mathematics, Physics, Chemistry, Biology, History, Geography, and Civics.
        
        STRICT OPERATIONAL GUIDELINES:
        1. LANGUAGE: Respond EXCLUSIVELY in {assigned_lang}. If the query is in Hindi/Hinglish, use pure Devanagari Hindi.
        2. NO GREETINGS: Do not say 'Namaste' or 'Hello'. Start explaining immediately.
        3. MATHEMATICAL PRECISION: Solve equations step-by-step.
        4. HISTORICAL ACCURACY: Provide dates and key figures clearly for subjects like History.
        5. VOCAL SYNC: Place a period (.) or (।) after every sentence or logical segment to assist the audio engine.
        6. IDENTITY: You are a male senior teacher. Always use masculine grammar (e.g., 'main samjha sakta hoon')."""

        messages = [{"role": "system", "content": system_protocol}]
        # Context window maintenance for coherent subject discussions
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Student Query: {query}. Provide a direct academic response in {assigned_lang}."})
        
        try:
            stream_response = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1
            )
            
            for chunk in stream_response:
                text_content = chunk.choices[0].delta.content
                if text_content:
                    yield text_content
                    # SYNC TRIGGER: Signal the UI to trigger audio at punctuation marks
                    if any(punc in text_content for punc in ['.', '!', '?', '।', '\n', '=', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as api_err:
            yield f"Mentor AI Error: {str(api_err)}"

# Singleton Instance for Global Accessibility
aura = AuraAssistant()
