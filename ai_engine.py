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
        # Latest High-Performance Model
        self.model = "llama-3.3-70b-versatile"
        try:
            # Multi-layered Security for API Access
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("Critical Error: GROQ_API_KEY not found in secrets.")
        except Exception as e:
            st.error(f"System Configuration Failure: {e}")

    def is_hindi(self, text):
        """Detects Devanagari script to switch between Madhur and Prabhat voices."""
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        Extensive text pre-processing to ensure mathematical clarity 
        and persona consistency. This prevents the voice engine from 
        tripping over complex symbols.
        """
        # Phase 1: Removing Documentation & Markdown Artifacts
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", " dollar ").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # Phase 2: Mathematical Phonetic Expansion (Crucial for Equations)
        # Isse voice engine ko har symbol bolne ka sahi samay milta hai
        math_map = {
            "²": " squared ",
            "^2": " squared ",
            "³": " cubed ",
            "^3": " cubed ",
            "+": " plus ",
            "-": " minus ",
            "=": " equals ",
            "x": " multiplied by ",
            "*": " multiplied by ",
            "/": " divided by ",
            "√": " square root of ",
            "π": " pi "
        }
        for sym, word in math_map.items():
            text = text.replace(sym, word)
            
        # Phase 3: Senior Academic Mentor Persona Alignment (Gender Corrections)
        gender_logic = {
            "sakti hoon": "sakta hoon", 
            "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon",
            "huu": "hoon",
            "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ",
            "main ek ai assistant hoon": "Main aapka senior academic mentor, Gyan Setu hoon"
        }
        for wrong, right in gender_logic.items():
            text = text.replace(wrong, right)
            
        return text

    async def _generate_voice_bytes(self, text):
        """High-speed asynchronous audio streaming directly to memory."""
        # Selecting the most natural Indian voices for academic context
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Optimized Rate (+15%) and Pitch for a commanding mentor-like voice
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-1Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """Base64 audio generator with robust thread-safe loop management."""
        clean_text = self.clean_text_for_speech(text)
        if not clean_text.strip():
            return None
            
        try:
            # Ensuring a dedicated event loop for each Streamlit session thread
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            audio_bytes = loop.run_until_complete(self._generate_voice_bytes(clean_text))
            return base64.b64encode(audio_bytes).decode()
        except Exception as e:
            # Silently logging for performance; error display handled by caller if needed
            print(f"Vocal Engine Error: {e}")
            return None

    def ask_stream(self, query, history):
        """
        AI Reasoning engine with streaming enabled. 
        Uses specific punctuation triggers to sync text with audio steps.
        """
        is_hindi_script = self.is_hindi(query)
        # Identifying intent to force correct script output
        roman_keywords = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kyun', 'kab', 'formula', 'solution']
        is_roman_hindi = any(word in query.lower() for word in roman_keywords)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        # High-Authority Persona Instructions
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        EXECUTIVE OPERATING PROCEDURES:
        1. STRICT LANGUAGE: Respond only in {forced_lang}.
        2. DIRECT RESPONSE: No greetings like "Hello" or "Namaste". No prefixes like "Aap" or "Student".
        3. MATHEMATICAL CLARITY: Break every equation into distinct steps. 
        4. PUNCTUATION SYNC: Use a full stop (.) or । after every number, equation step, or logic block.
        5. TONE: Scholarly, professional, and precise.
        6. SCRIPT: Never use Roman Hindi. Use pure Devanagari for Hindi."""

        messages = [{"role": "system", "content": system_instruction}]
        # Maintaining context window of last 4 interactions
        messages.extend(history[-4:]) 
        messages.append({"role": "user", "content": f"Academic Task: {query}. Respond in {forced_lang} directly."})
        
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
                    # SYNC_SIGNAL triggers the audio engine for the current accumulated chunk
                    # Added '=' and '\n' to better handle math equations and lists
                    if any(punc in content for punc in ['.', '!', '?', '।', '\n', '=', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Core Processing Error: {str(e)}"

# Singleton Instance for Global Access
aura = AuraAssistant()
