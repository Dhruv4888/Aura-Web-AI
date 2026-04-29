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
        Gyan Setu Core Initialization.
        Focuses on high-performance model selection and API security.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            # High Priority Security Check for API Access
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("Critical Failure: GROQ_API_KEY is missing in session secrets.")
        except Exception as e:
            st.error(f"Mentor Engine Boot Error: {e}")

    def is_hindi(self, text):
        """
        Detection of Devanagari script to ensure perfect voice selection 
        between Madhur (Hindi) and Prabhat (English).
        """
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        ULTIMATE PHONETIC EXPANSION LOGIC:
        This section is expanded to ensure that math equations are not just read, 
        but 'explained' with proper pauses.
        """
        # Step 1: Scrubbing Technical/Markdown Overheads
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Step 2: High-Resolution Mathematical Mapping (Deep Expansion)
        # We add commas and spaces to force the TTS engine to slow down on symbols.
        math_expansion_map = {
            "²": " squared, ",
            "^2": " squared, ",
            "³": " cubed, ",
            "^3": " cubed, ",
            "x": " multiplied by ",
            "*": " multiplied by ",
            "+": " plus ",
            "-": " minus ",
            "=": " equals to ",
            "/": " divided by ",
            "√": " square root of ",
            "π": " pi ",
            "3x": "3 x", 
            "2x": "2 x",
            "4x": "4 x",
            "5x": "5 x",
            "0": "zero",
            "(": " open bracket, ",
            ")": " close bracket, "
        }
        
        for symbol, phonetic_word in math_expansion_map.items():
            text = text.replace(symbol, phonetic_word)
            
        # Step 3: Persona Consistency & Gender-Specific Grammar Corrections
        # Ensuring the 'Senior Academic Mentor' identity stays solid.
        academic_persona_corrections = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ",
            "main ek machine hoon": "Main aapka senior academic mentor, Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon, aapka shikshak"
        }
        
        for error, fix in academic_persona_corrections.items():
            text = text.replace(error, fix)
            
        return text

    async def _generate_voice_bytes(self, text):
        """
        RAM-Resident Vocal Synthesis.
        Optimized for high-fidelity audio generation without disk latency.
        """
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Rate set to +10% (Slightly slower than before for better math clarity)
        # Pitch kept slightly low for a professional, mature mentor tone.
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-1Hz")
        
        audio_stream = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream += chunk["data"]
        return audio_stream

    def get_audio_data(self, text):
        """
        Thread-Safe Audio Exporter for Streamlit.
        Manages event loops to prevent async collisions during speech.
        """
        cleaned_payload = self.clean_text_for_speech(text)
        if not cleaned_payload.strip():
            return None
            
        try:
            # Ensuring localized event loops for each concurrent user thread
            try:
                current_loop = asyncio.get_event_loop()
            except RuntimeError:
                current_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(current_loop)
            
            audio_raw = current_loop.run_until_complete(self._generate_voice_bytes(cleaned_payload))
            return base64.b64encode(audio_raw).decode()
        except Exception as processing_error:
            print(f"TTS Engine Processing Failure: {processing_error}")
            return None

    def ask_stream(self, query, history):
        """
        Advanced Reasoning & Streaming Engine.
        Uses punctuation-based chunking for synchronized text-to-vocal delivery.
        """
        # Language Context Detection
        is_hindi_input = self.is_hindi(query)
        roman_indic_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'formula', 'answer']
        is_romanized_hindi = any(word in query.lower() for word in roman_indic_keywords)
        
        assigned_lang = "HINDI (Devanagari Script)" if (is_hindi_input or is_romanized_hindi) else "ENGLISH"
        
        # SYSTEM PROTOCOL - DEFINING THE MENTOR BEHAVIOR
        system_protocol = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        OPERATIONAL GUIDELINES:
        1. MANDATORY LANGUAGE: Respond exclusively in {assigned_lang}.
        2. NO PREFIXES: Never start with "Hello," "Student," or "Ji". Go straight to the answer.
        3. MATHEMATICAL PRECISION: When solving equations (e.g., 3x² - 2x + 50 = 0), explain each step.
        4. VOCAL SYNC: You must place a period (.) or (।) after every equation symbol or distinct logic step.
        5. TONE: Expert, scholarly, and professional.
        6. SCRIPT: Use pure Devanagari for Hindi; strictly forbid Romanized Hindi."""

        messages = [{"role": "system", "content": system_protocol}]
        # Maintaining short-term context window for performance
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Student Query: {query}. Provide direct solution in {assigned_lang}."})
        
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
                    # SYNC TRIGGER: Breaking at punctuation or mathematical conclusions
                    if any(p in text_content for p in ['.', '!', '?', '।', '\n', '=', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as api_err:
            yield f"Mentor AI Error: {str(api_err)}"

# Singleton Pattern for Global Accessibility
aura = AuraAssistant()
