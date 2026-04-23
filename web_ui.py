import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import mic_recorder

st.title("AURA (Voice Mode)")

# Voice Input Section
audio = mic_recorder(start_prompt="Click to Speak", stop_prompt="Stop Recording", key='recorder')

if audio:
    # Yahan hum user ki voice ko text mein badal rahe hain
    st.audio(audio['bytes']) 
    st.write("Processing your voice...")
    # Aura logic call karein
    response = aura.ask("Please reply to my voice command") # Example logic
    st.write(f"Aura: {response}")
    aura.speak(response)
