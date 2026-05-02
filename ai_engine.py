import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64
import io
import time

class AuraAssistant:
    def __init__(self):
        """
        Gyan Setu Core Engine Initialization.
        Focus: Maximum stability, high-speed response, and strict termination.
        Enhanced: Precision timing for alphabet-level streaming.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            # High-priority API key retrieval for faster authentication
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("System Error: GROQ_API_KEY is not defined in the secrets.")
        except Exception as e:
            st.error(f"Critical Boot Failure: {e}")

    def is_hindi(self, text):
        """
        Advanced Devanagari script detection.
        Scans for the specific unicode range used in Hindi.
        """
        if not text:
            return False
        # Unicode range for Devanagari: \u0900 to \u097F
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        ULTIMATE PHONETIC RE-ENGINEERING (STRICT MENTOR TONE):
        Optimized to handle complex Math, Science, and History narratives.
        """
        # Quick-strip technical artifacts and formatting
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # High-Speed Mathematical Phonetic Mapping
        math_map = {
            "²": " square, ",
            "^2": " square, ",
            "³": " cube, ",
            "^3": " cube, ",
            "x²": " x square, ",
            "x^2": " x square, ",
            " + ": " plus ",
            " - ": " minus ",
            " = ": " equals to ",
            " / ": " divided by ",
            " * ": " ", 
            " x ": " ", 
            "2x": " 2 x ", 
            "3x": " 3 x ",
            "4x": " 4 x ",
            "5x": " 5 x ",
            "√": " square root of ",
            "π": " pi ",
            "(": " bracket start ",
            ")": " bracket close "
        }
        
        # Batch replacement for high-concurrency performance
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)

        # Senior Mentor Persona Correction (Strictly Male Academic Voice)
        gender_fix = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ",
            "main ek machine hoon": "Main Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon"
        }
        
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
            
        return text

    async def _generate_voice_bytes(self, text):
        """
        Asynchronous Voice Synthesis via Edge-TTS.
        Configured for 1.1x speed (Academic Efficiency) with authoritative pitch.
        """
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Rate slightly increased (+10%) to match the faster generation logic
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-2Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """
        High-Concurrency Audio Interface.
        Converts logical text blocks into base64 vocal packets for UI injection.
        """
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip():
            return None
            
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_raw = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_raw).decode()
        except Exception as e:
            print(f"Vocal Processing Error: {e}")
            return None

    def stream_alphabets(self, text):
        """
        ULTRA-GRANULAR CHARACTER GENERATOR.
        This function breaks down LLM tokens into individual characters.
        A controlled delay is injected to force the UI to render 'one-by-one'.
        """
        if not text:
            return
            
        for char in text:
            # Yielding each alphabet to the main stream
            yield char
            # Critical Delay: 0.02s ensures visibility of the 'typing' effect
            time.sleep(1.82)

    def ask_stream(self, query, history):
        """
        The Reasoning Core (STRICT TERMINATION LOGIC). 
        Now fully integrated with alphabet-level streaming for visual sync.
        """
        # Improved Detection: Direct Hindi characters or common Hinglish markers
        is_hindi_in = self.is_hindi(query)
        hinglish_markers = [" btao", " batiye", " hai", " tha", " batao", " kya", " kaise"]
        is_hinglish = any(m in query.lower() for m in hinglish_markers)
        
        # Solidifying the forced language protocol
        if is_hindi_in or is_hinglish:
            forced_lang = "HINDI (Strictly Devanagari Script)"
            language_style = "Use Shudh Hindi, strictly avoid English alphabets in response."
        else:
            forced_lang = "ENGLISH"
            language_style = "Use formal academic English."
        
        # SYSTEM PROTOCOL - REINFORCED VERSION
        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor.
        RESPONSE PROTOCOL:
        1. LANGUAGE: {forced_lang}. {language_style}
        2. CONTENT: Answer ONLY the specific academic question. No conversational filler.
        3. LENGTH: Maximum 3 to 5 logical sentences. For Math, show steps clearly.
        4. TERMINATION: Do not ask follow-up questions. Finish and STOP.
        5. SYNC: Put a period (.) or (। ) after EVERY sentence to signal the audio engine.
        6. PERSONA: You are a male teacher. Use formal, authoritative language."""

        messages = [{"role": "system", "content": system_instruction}]
        
        # Optimized context window: Only 2 turns to prevent 'history looping'
        messages.extend(history[-2:]) 
        messages.append({"role": "user", "content": f"Student Query: {query}. (Provide a concise answer and stop.)"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1, 
                max_tokens=450, 
                stop=["Student Query:", "Student:", "\n\n\n"] 
            )
            
            for chunk in completion:
                token_text = chunk.choices[0].delta.content
                if token_text:
                    # Execute alphabet-level generator for every token received
                    # This creates the 'one-by-one' visual effect on the screen
                    for alphabet in self.stream_alphabets(token_text):
                        yield alphabet
                    
                    # Logic Gate for Sync: Trigger audio processing on sentence completion
                    if any(p in token_text for p in ['.', '!', '?', '।', '\n', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Computational Failure: {str(e)}"

# Global instance for UI integration
aura = AuraAssistant()
