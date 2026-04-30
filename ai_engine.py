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
        Focus: Maximum stability, high-speed response, and strict termination.
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
        text = re.sub(r'\\[WIKI_SEARCH:.*?\\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\\\text\\{.*?\\}', '', text) 
        
        # High-Speed Mathematical Phonetic Mapping
        math_map = {
            "²": " square, ", "^2": " square, ", "³": " cube, ", "^3": " cube, ",
            "x²": " x square, ", "x^2": " x square, ", " + ": " plus ", " - ": " minus ",
            " = ": " equals to ", " / ": " divided by ", " * ": " ", " x ": " ",
            "2x": " 2 x ", "3x": " 3 x ", "4x": " 4 x ", "5x": " 5 x ",
            "√": " square root of ", "π": " pi ", "(": " bracket start ", ")": " bracket close "
        }
        
        # Batch replacement for high-concurrency performance
        for symbol, word in math_map.items():
            text = text.replace(symbol, word)

        # Senior Mentor Persona Correction (Strictly Male Academic Voice)
        gender_fix = {
            "sakti hoon": "sakta hoon", "karti hoon": "karta hoon", 
            "rahi hoon": "raha hoon", "huu": "hoon", "kar rahi hun": "kar raha hoon",
            "hun ": "hoon ", "main ek machine hoon": "Main Gyan Setu hoon",
            "main ek ai hoon": "Main Gyan Setu hoon"
        }
        
        for wrong, right in gender_fix.items():
            text = text.replace(wrong, right)
            
        return text.strip()

    async def _generate_voice_stream(self, text, chunk_id):
        """
        TRUE STREAMING TTS - Real-time audio chunks.
        """
        if len(text) < 3:  # Skip very short text
            return
            
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+10%", pitch="-2Hz")
        
        audio_buffer = b""
        chunk_count = 0
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer += chunk["data"]
                # Stream every 2KB for smooth playback
                if len(audio_buffer) >= 2048:
                    yield {
                        "type": "audio",
                        "data": base64.b64encode(audio_buffer).decode(),
                        "id": f"{chunk_id}_{chunk_count}"
                    }
                    audio_buffer = b""
                    chunk_count += 1
        
        # Final chunk
        if audio_buffer:
            yield {
                "type": "audio",
                "data": base64.b64encode(audio_buffer).decode(),
                "id": f"{chunk_id}_{chunk_count}"
            }

    async def stream_audio_realtime(self, text_generator):
        """
        MAIN TRUE STREAMING ENGINE: Text → Audio sync.
        Processes token-by-token text into immediate audio.
        """
        text_buffer = ""
        sentence_buffer = ""
        audio_chunk_id = 0
        
        async for text_chunk in text_generator:
            text_buffer += text_chunk
            
            # Visual streaming (token level)
            yield {
                "type": "text",
                "data": text_chunk,
                "full_text": text_buffer
            }
            
            # Sentence detection for natural TTS breaks
            sentences = re.split(r'[.!?।\n]+', sentence_buffer + text_chunk)
            sentence_buffer = sentences[-1]  # Keep last incomplete sentence
            
            for complete_sentence in sentences[:-1]:
                clean_sentence = self.clean_text_for_speech(complete_sentence.strip())
                if len(clean_sentence) > 5:  # Minimum length
                    # IMMEDIATE TTS streaming
                    async for audio_chunk in self._generate_voice_stream(clean_sentence, audio_chunk_id):
                        yield audio_chunk
                    audio_chunk_id += 1
        
        # Final sentence
        if sentence_buffer.strip():
            clean_final = self.clean_text_for_speech(sentence_buffer.strip())
            if len(clean_final) > 5:
                async for audio_chunk in self._generate_voice_stream(clean_final, audio_chunk_id):
                    yield audio_chunk

    def ask_stream(self, query, history):
        """
        FIXED: Returns proper async iterable generator for Streamlit.
        """
        # Language detection (same logic)
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
                stop=["Student Query:", "Student:", "\\n\\n\\n"] 
            )
            
            # FIXED: Proper async generator pattern for Streamlit
            async def groq_text_stream():
                """True async generator - token by token"""
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        yield content
                    await asyncio.sleep(0)  # Yield control for smooth streaming
            
            return groq_text_stream()
            
        except Exception as e:
            async def error_stream():
                yield f"Computational Failure: {str(e)}"
            return error_stream()

# Global instance for UI integration
aura = AuraAssistant()
