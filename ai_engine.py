# ai_engine.py
import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st
import base64


class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        try:
            if "GROQ_API_KEY" in st.secrets:
                self.api_key = st.secrets["GROQ_API_KEY"]
                self.client = Groq(api_key=self.api_key)
            else:
                st.error("System Error: GROQ_API_KEY is not defined in the secrets.")
        except Exception as e:
            st.error(f"Critical Boot Failure: {e}")

    def is_hindi(self, text):
        if not text:
            return False
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text{.*?}', '', text) 

        # Math symbols
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
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)

        # Gender fix (male mentor)
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
        if not text.strip():
            return b""

        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-2Hz")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    def get_audio_data(self, text):
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
            if not audio_raw:
                return None
            return base64.b64encode(audio_raw).decode()
        except Exception as e:
            print(f"Vocal Processing Error: {e}")
            return None

    def ask_stream(self, query, history):
        is_hindi_in = self.is_hindi(query)
        hinglish_markers = [" btao", " batiye", " hai", " tha", " batao", " kya", " kaise"]
        is_hinglish = any(m in query.lower() for m in hinglish_markers)

        if is_hindi_in or is_hinglish:
            forced_lang = "HINDI (Strictly Devanagari Script)"
            language_style = "Use Shudh Hindi, strictly avoid English alphabets in response."
        else:
            forced_lang = "ENGLISH"
            language_style = "Use formal academic English."

        system_instruction = f"""You are 'Gyan Setu', a Senior Academic Mentor.
        RESPONSE PROTOCOL:
        1. LANGUAGE: {forced_lang}. {language_style}
        2. CONTENT: Answer ONLY the specific academic question. No conversational filler.
        3. LENGTH: Maximum 3 to 5 logical sentences. For Math, show steps clearly.
        4. TERMINATION: Do not ask follow-up questions. Finish and STOP.
        5. SYNC: Put a period (.) or (।) after EVERY step or sentence to signal the audio engine.
        6. PERSONA: You are a male teacher. Use formal, authoritative language."""

        messages = [{"role": "system", "content": system_instruction}]
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
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    if any(p in content for p in ['.', '!', '?', '।', '\n', ':', ';']):
                        yield "||SYNC_SIGNAL||"
        except Exception as e:
            yield f"Computational Failure: {str(e)}"


aura = AuraAssistant()
