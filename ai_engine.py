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
        Focus: Maximum stability and high-speed response for Classes 1-12.
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
        Devanagari script detection.
        Optimized regex for faster linguistic scanning.
        """
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        """
        ULTIMATE PHONETIC RE-ENGINEERING (HIGH-SPEED VERSION):
        Optimized to handle complex Math and Science without lag.
        """
        # Quick-strip technical artifacts
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        # High-Speed Mathematical Phonetic Mapping
        # Focused on natural pauses to prevent overlapping.
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
        
        # Batch replacement for performance
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
            "main ek machine hoon": "Main Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon"
        }
        
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
            
        return text

    async def _generate_voice_bytes(self, text):
        """
        Asynchronous Voice Synthesis.
        Optimized for clarity and professional academic tone.
        """
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Rate +10% for slightly faster but clear academic delivery
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-2Hz")
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
        """
        High-Concurrency Audio Interface.
        Reduced overhead for faster byte-to-base64 conversion.
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
        The Reasoning Core (To-The-Point Logic). 
        Updated to force concise, accurate academic answers.
        """
        is_hindi_in = self.is_hindi(query)
        # Faster language detection logic
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_in or " btao" in query.lower() or " hai" in query.lower()) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor.
        CONCISE RESPONSE PROTOCOL:
        1. Accuracy: Give direct, accurate answers for Class 1-12 subjects.
        2. No Fluff: Do NOT explain background unless asked. Do NOT give long introductions.
        3. Language: Respond strictly in {forced_lang}.
        4. Math: Provide step-by-step solutions but keep them crisp. Put (.) after each step.
        5. Sync: Use (.) or (।) after symbols like '=' or '+' for audio pauses.
        6. Persona: Maintain a professional male teacher identity."""

        messages = [{"role": "system", "content": system_instruction}]
        # Using a shorter context window for faster processing (Last 3 turns)
        messages.extend(history[-3:]) 
        messages.append({"role": "user", "content": f"Directly answer this: {query}."})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.1,
                max_tokens=1024 # Prevents unnecessarily long generation
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Signal for audio break
                    if any(p in content for p in ['.', '!', '?', '।', '\n', '=', ':', ';']):
                        yield "||SYNC_SIGNAL||"
                        
        except Exception as e:
            yield f"Computational Failure: {str(e)}"

# Global instance
aura = AuraAssistant()
