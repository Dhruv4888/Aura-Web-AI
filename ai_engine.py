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

    async def _generate_voice(self, text, filename):
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        # Teacher mode ke liye speed (+5%) thodi kam rakhi hai taaki clear sunai de
        communicate = edge_tts.Communicate(text, selected_voice, rate="+5%", pitch="-2Hz")
        await communicate.save(filename)

    def speak(self, text):
        # Voice Cleanup: Markdown aur LaTeX symbols ko bolne se rokne ke liye
        clean_text = re.sub(r'\[WIKI_SEARCH:.*?\]', '', text) # Wiki tags hataye
        clean_text = clean_text.replace("$", "").replace("#", "").replace("*", "").replace("`", "")
        
        # Strict Gender Correction
        corrections = {"sakti hoon": "sakta hoon", "karti hoon": "karta hoon", "rahi hoon": "raha hoon"}
        clean_text = clean_text.lower()
        for wrong, right in corrections.items():
            clean_text = clean_text.replace(wrong, right)
        
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except: pass

    def ask(self, query, history):
        try:
            # GYAN SETU PROMPT INTEGRATION
            base_prompt = """You are Gyan Setu — a warm, patient teacher who explains things in DEEP, DESCRIPTIVE detail using RICH MARKDOWN.

YOUR TEACHING APPROACH:
0. VISUAL REFERENCE: For every response, identify the primary educational topic(s). Generate a tag: [WIKI_SEARCH: Topic Name] at the start.
1. ALWAYS give VERY DETAILED explanations with examples and step-by-step working.
2. Break concepts into small pieces.
3. Use real-world examples and analogies.
4. FOR MATH & SCIENCE: Use proper LaTeX for formulas ($$ for block, $ for inline).
5. FOR CODE: Use triple backtick code blocks with language name.
6. Format in professional markdown (##, ###, bold, bullets).
7. Use simple, warm language — imagine explaining to a curious student.
8. Be encouraging: "Great question!", "Let me show you step by step".
9. Include examples, analogies, and practice questions.
10. STRICT SCOPE RULE: If user asks anything not related to school topics (classes 1-12) or general education, do not answer that content. Reply exactly with: "Please ask from your subject questions only." """

            messages = [{"role": "system", "content": base_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": query})

            chat_completion = self.client.chat.completions.create(messages=messages, model=self.model)
            return chat_completion.choices[0].message.content
        except:
            return "Connection lost, Sir."

aura = AuraAssistant()
