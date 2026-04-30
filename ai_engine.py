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
                st.error("GROQ_API_KEY missing in secrets")
        except Exception as e:
            st.error(f"Init Error: {e}")

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text or ''))

    def clean_text_for_speech(self, text):
        if not text: return ""
        text = re.sub(r'\\[WIKI_SEARCH:.*?\\]', '', text)
        text = text.replace("$", "#", "*", "`", "", 1)
        text = re.sub(r'\\\\text\\{.*?\\}', '', text)
        
        math_map = {"²": " square", "^2": " square", " + ": " plus ", " = ": " equals "}
        for k, v in math_map.items():
            text = text.replace(k, v)
            
        gender_fix = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon"}
        for k, v in gender_fix.items():
            text = text.replace(k, v)
        return text.strip()

    def ask_stream(self, query, history):
        """
        *** FIXED: SYNCHRONOUS GENERATOR for Streamlit for loop ***
        """
        # Language detection
        is_hindi = self.is_hindi(query) or any(m in query.lower() for m in ["btao", "batao", "kya"])
        lang = "HINDI" if is_hindi else "ENGLISH"
        
        system_prompt = f"""You are Gyan Setu, Senior Academic Mentor.
        LANGUAGE: {lang}
        Answer ONLY the question in 3-5 sentences. End with period.
        Male teacher voice. Stop after answer."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model, messages=messages, stream=True,
                temperature=0.1, max_tokens=450
            )
            
            # *** SYNCHRONOUS ITERATOR (Streamlit compatible) ***
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content
                    
        except Exception as e:
            yield f"Error: {e}"

aura = AuraAssistant()
