import os
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
            st.error("API Key error! Please check your secrets.")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def ask_stream(self, query, history):
        is_hindi_script = self.is_hindi(query)
        roman_hindi_words = ['kya', 'hai', 'kaise', 'batao', 'samjhao', 'kise', 'kyun']
        is_roman_hindi = any(word in query.lower() for word in roman_hindi_words)
        
        forced_lang = "HINDI (Devanagari Script)" if (is_hindi_script or is_roman_hindi) else "ENGLISH"
        
        system_instruction = f"""You are 'Gyan Setu', a formal Senior Academic Mentor.
        STRICT OPERATING RULES:
        1. LANGUAGE: Respond 100% in {forced_lang} ONLY.
        2. NO HINGLISH: If in HINDI, use ONLY Devanagari script.
        3. TONE: Professional, formal, and academic. Use 'Aap'.
        4. FORMAT: Keep sentences concise for better speech synchronization."""

        messages = [{"role": "system", "content": system_instruction}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": f"Student Question: {query}\n\n(Note: Reply strictly in {forced_lang}.)"})
        
        try:
            completion = self.client.chat.completions.create(
                messages=messages, 
                model=self.model,
                stream=True,
                temperature=0.0,
                top_p=0.1
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    # Sentence break detection for synchronization
                    if any(punc in content for punc in ['.', '?', '!', '।', '\n']):
                        yield "||SYNC_SPEECH||"
                        
        except Exception as e:
            yield f"Error: {str(e)}"

aura = AuraAssistant()
