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
        # Swararaaj ya Madhur ko tweak karke behtar sound karwana
        selected_voice = "hi-IN-MadhurNeural" if self.is_hindi(text) else "en-IN-PrabhatNeural"
        
        # Rate +15% (fast) aur Pitch -2Hz (deep male voice) robotic sound kam karne ke liye
        communicate = edge_tts.Communicate(text, selected_voice, rate="+15%", pitch="-2Hz")
        await communicate.save(filename)

    def speak(self, text):
        # Gender Correction: Kisi bhi haal mein female words ko male mein badalna
        corrections = {
            "sakti hoon": "sakta hoon",
            "karti hoon": "karta hoon",
            "rahi hoon": "raha hoon",
            "hoon main ek female": "hoon main ek male",
            "ladki hoon": "ladka hoon",
            "assistant hoon": "male assistant hoon"
        }
        
        clean_text = text.lower()
        for wrong, right in corrections.items():
            clean_text = clean_text.replace(wrong, right)
        
        clean_text = clean_text.replace("*", "").replace("#", "")
        
        filename = "aura_voice.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            with open(filename, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
            if os.path.exists(filename): os.remove(filename)
        except:
            pass

    def ask(self, query):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "Strict Instruction: You are AURA, a MALE AI. Always use 'karta hoon', 'raha hoon', 'sakta hoon'. You are NOT a female. Reply in short sentences."
                    },
                    {"role": "user", "content": query}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except:
            return "Server error, Sir."

aura = AuraAssistant()
