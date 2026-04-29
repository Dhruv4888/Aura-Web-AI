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
        Gyan Setu Core Engine Initialization.
        Focus: Maximum stability for high-computational math tasks.
        """
        self.model = "llama-3.3-70b-versatile"
        try:
            # Ensuring the API key is retrieved with high priority
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("System Error: GROQ_API_KEY is not defined in the secrets environment.")
        except Exception as e:
            st.error(f"Critical Boot Failure: {e}")

    def is_hindi(self, text):
        """
        Devanagari script detection for regional voice modulation.
        Ensures the mentor speaks in the correct linguistic tone.
        """
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        ULTIMATE PHONETIC RE-ENGINEERING:
        Bhai, yahan maine 'multiply' word hata diya hai kyunki wo overlapping badha raha tha.
        Ab ye '2x' ko 'Two Ex' ki tarah natural bolega.
        """
        # Removing technical artifacts
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Step-by-Step Mathematical Phonetic Refinement
        # Maine 'multiplied by' hata kar simple spaces aur commas dale hain taaki natural pauses milein.
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
            " * ": " ", # Removed 'multiplied by' for speed and natural flow
            " x ": " ", # Standard 'x' symbol becomes a natural pause
            "2x": " 2 x ", # Forcing space for natural 'Two Ex' sound
            "3x": " 3 x ",
            "4x": " 4 x ",
            "5x": " 5 x ",
            "√": " square root of ",
            "π": " pi ",
            "(": " bracket start ",
            ")": " bracket close "
        }
        
        # Applying the map twice to handle overlapping symbols in the text
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)

        # Senior Mentor Persona Correction (Strictly Male Gender)
        gender_fix = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ",
            "main ek machine hoon": "Main aapka senior mentor, Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon"
        }
        
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
            
        return text

    async def _generate_voice_bytes(self, text):
        """
        Asynchronous Stream Generation.
        Rate is set to +8% (even slower) for maximum mathematical clarity.
        """
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Pitch lowered for authority, Rate slowed down for equation clarity
        communicate = edge_tts.Communicate(text, selected_voice, rate="+8%", pitch="-2Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """
        Thread-safe Audio Interface.
        Ensures consistent audio generation even under heavy server load.
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

    def ask_stream(self, query, history):
        """
        The Reasoning Core. 
        Forces the AI to add punctuation after every symbol to help the sync engine.
        """
        is_hindi_in = self.is_hindi(query)
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_in or "hai" in query.lower()) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        CORE SYNC PROTOCOLS:
        1. Language: {forced_lang}.
        2. Math Formatting: Put a full stop (.) after every single step or result. 
        3. Equations: Never write long strings. Write '2x square' as '2x^2'. 
        4. Tone: Very professional, scholarly. No casual talk.
        5. Breaks: You MUST include a period (.) or (।) after '=' and '+' signs to allow audio syncing.
        6. Persona: Maintain a strict male academic mentor identity."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Problem: {query}. Solve and respond in {forced_lang}."})
        
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
                    # Breaking for audio on every logical delimiter
                    if any(p in content for p in ['.', '!', '?', '।', '\n', '=', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Computational Failure: {str(e)}"

# Global instance for web_ui access
aura = AuraAssistant()
