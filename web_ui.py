import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time

# --- OLD UI CONFIG & CSS ---
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #0b0e14 !important; }
    h1 { color: #00fbff !important; font-family: 'Orbitron', sans-serif !important; text-align: center !important; font-size: 50px !important; text-shadow: 0 0 20px #00fbff; margin-top: -50px; }
    button[data-testid="stBaseButton-secondary"] { background-color: #00fbff !important; color: #0b0e14 !important; border-radius: 100px !important; width: 180px !important; height: 180px !important; border: 8px solid #1a202c !important; font-family: 'Orbitron', sans-serif !important; font-weight: bold !important; display: block !important; margin: 0 auto !important; box-shadow: 0 0 30px rgba(0, 251, 255, 0.4) !important; }
    .chat-container { background: #1a202c; padding: 20px; border-radius: 15px; border-left: 5px solid #00fbff; color: white; margin-top: 20px; font-family: 'Arial', sans-serif; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

text = speech_to_text(start_prompt="TAP TO ASK", stop_prompt="LISTENING...", language='en-IN', use_container_width=True, just_once=True, key='gyansetu_mic')

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    
    # --- NEW LOGIC IN OLD UI ---
    with st.spinner("Gyan Setu is thinking..."):
        full_response = ""
        # Empty placeholder for typing effect inside old container style
        container = st.empty()
        
        for chunk in aura.ask_stream(text, st.session_state.messages):
            full_response += chunk
            container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}▌</div>', unsafe_allow_html=True)
            time.sleep(0.01)
        
        # Final render without cursor
        container.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_response}</div>', unsafe_allow_html=True)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        aura.speak(full_response)
