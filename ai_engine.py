import os
import pygame
import asyncio
import edge_tts
import speech_recognition as sr
from groq import Groq
import re
import pyautogui
import webbrowser
import subprocess
import time # Naya import timestamp ke liye
import streamlit as st

pygame.mixer.init()

class AuraAssistant:
    def __init__(self):
        # Yahan apni Groq key daalein
        self.api_key = st.secrets["GROQ_API_KEY"]
        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Setup Error: {e}")
            
        self.model = "llama-3.3-70b-versatile"
        self.recognizer = sr.Recognizer()

    def is_hindi(self, text):
        return bool(re.search(r'[\u0900-\u097F]', text))

    def listen(self):
        with sr.Microphone() as source:
            print("\n[LISTENING...]")
            self.recognizer.pause_threshold = 0.8
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                query = self.recognizer.recognize_google(audio, language='en-in')
                print(f"User: {query}")
                return query.lower()
            except Exception:
                return ""

    async def _generate_voice(self, text, filename):
        if self.is_hindi(text):
            selected_voice = "hi-IN-MadhurNeural"
            rate, pitch = "+0%", "+0Hz"
        else:
            selected_voice = "en-IN-PrabhatNeural"
            rate, pitch = "+10%", "-3Hz"

        communicate = edge_tts.Communicate(text, selected_voice, rate=rate, pitch=pitch)
        await communicate.save(filename)

    def speak(self, text):
        clean_text = text.replace("*", "").replace("#", "")
        print(f"[AURA]: {clean_text}")
        filename = "speech.mp3"
        try:
            asyncio.run(self._generate_voice(clean_text, filename))
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            if os.path.exists(filename): os.remove(filename)
        except Exception as e:
            print(f"Voice Error: {e}")

    def generate_and_save_code(self, user_query):
        try:
            prompt = f"Write only the Python code for: {user_query}. Do not include explanations or markdown. Just the raw code."
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
            )
            raw_code = completion.choices[0].message.content
            clean_code = raw_code.replace("```python", "").replace("```", "").strip()
            
            filename = "aura_generated_task.py"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(clean_code)
            return filename
        except Exception as e:
            return None

    def execute_tools(self, query):
        # --- UPDATE: "lo" word hata diya hai kyunki wo Hindi conversation mein baar baar aata hai ---
        if "screenshot" in query or "snap" in query or "capture" in query:
            ts = time.strftime("%Y%m%d-%H%M%S")
            filename = f"Aura_Snap_{ts}.png"
            pyautogui.screenshot(filename)
            return f"Done Sir, screenshot saved as {filename}."

        # 2. YouTube / Chrome Logic
        elif "youtube" in query or "play" in query or "chalao" in query:
            song = query.replace("play", "").replace("youtube", "").replace("chalao", "").replace("par", "").strip()
            url = f"https://www.youtube.com/results?search_query={song}"
            
            # Chrome Path (Windows Default)
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
            
            try:
                webbrowser.get(chrome_path).open(url)
                return f"Opening {song} on YouTube in Chrome, Sir."
            except:
                webbrowser.open(url)
                return f"Opening YouTube for {song}."

        # 3. App Opener (Paint/Chrome)
        elif "open chrome" in query:
            subprocess.Popen(["C:/Program Files/Google/Chrome/Application/chrome.exe"])
            return "Opening Google Chrome, Sir."

        # 4. Code Generation
        elif "code for" in query or "script" in query:
            self.speak("Sure Sir, generating the code. Please wait.")
            filename = self.generate_and_save_code(query)
            if filename:
                return f"I have saved the code in {filename}. Should I run it?"
            return "Sorry Sir, I couldn't generate the code."

        # 5. Run the generated file
        elif "run this code" in query or ("chalao" in query and "file" in query):
            if os.path.exists("aura_generated_task.py"):
                subprocess.Popen(["python", "aura_generated_task.py"])
                return "Executing the code now, Sir."
            return "No file found to run."

        return None

    def ask(self, query):
        if not query: return ""
        
        tool_response = self.execute_tools(query)
        if tool_response:
            return tool_response

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Aura, a professional AI. If user speaks in Hindi, reply ONLY in Hindi script. If English, reply in English. Keep it concise."
                    },
                    {"role": "user", "content": query}
                ],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return "Sir, connection error."

aura = AuraAssistant()