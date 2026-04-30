import os
from groq import Groq
import re
import streamlit as st

class AuraAssistant:
    def __init__(self):
        """
        Lightweight Engine optimized for Browser-Side Speech Synthesis.
        """
        self.model = "llama-3.3-70b-versatile"
        self.api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY", "")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def ask_stream(self, query, history):
        """
        Pure Text Streamer. No internal TTS processing to ensure 0% lag.
        """
        is_hindi = self.is_hindi(query)
        lang_gate = "Hindi script" if is_hindi else "English"
        
        system_msg = f"You are Gyan Setu. Answer strictly in {lang_gate}. Max 2 short sentences. Be direct."
        
        messages = [{"role": "system", "content": system_msg}]
        messages.extend(history[-2:])
        messages.append({"role": "user", "content": query})

        try:
            completion = self.client.chat.completions.create(
                messages=messages, model=self.model, stream=True, temperature=0.3
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            yield f"Error: {str(e)}"

aura = AuraAssistant()
