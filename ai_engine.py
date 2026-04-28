import os
import asyncio
import edge_tts
from groq import Groq
import re
import streamlit as st

class AuraAssistant:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"
        try:
            self.api_key = st.secrets["GROQ_API_KEY"]
            self.client = Groq(api_key=self.api_key)
        except:
            st.error("API Key error!")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def clean_text_for_speech(self, text):
        text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text)
        text = text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        text = re.sub(r'\\text\{.*?\}', '', text) 
        
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        communicate = edge_tts.Communicate(text, selected_voice, rate="+12%", pitch="-1Hz")
        await communicate.save(filename)

    def speak(self, text):
        """Modified speak to handle single sentences for faster sync"""
        clean_text = self.clean_text_for_speech(text)
        # Unique filename to avoid file-in-use errors during rapid sentences
        filename = f"temp_voice_{hash(clean_text)}.mp3"
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._generate_voice(clean_text, filename))
            
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask_stream(self, query, history):
        is_hindi_script = self.is_hindi(query)
        roman_hindi_words = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kise', 'kyun', 'kya hai']
        is_roman_hindi = any(word in query.lower() for word in roman_hindi_words)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT OPERATING RULES:
        1. LANGUAGE: Respond 100% in {forced_lang} ONLY. 
        2. NO HINGLISH: Use Devanagari for Hindi. No English alphabets in Hindi mode.
        3. TONE: Professional, formal, use 'Aap'.
        4. FORMAT: Short sentences. Use bullet points. No unnecessary greetings."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": f"Student Question: {query}\n\n(Note: Reply strictly and entirely in {forced_lang}.)"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.0, 
                top_p=0.1
            )
            
            full_sentence = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    full_sentence += content
                    yield content
                    
                    # Sir's Logic: Trigger when a sentence-ending punctuation is found
                    if any(punc in content for punc in ['.', '?', '!', '\n', '।']):
                        # We yield a special marker to tell UI to play audio
                        yield "||SENTENCE_COMPLETE||"
                        
        except:
            yield "Kshama karein, sampark mein badha hai."

aura = AuraAssistant()
