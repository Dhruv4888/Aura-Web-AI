import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="AURA AI", page_icon="🎙️")

# CSS: Wahi Orbitron aur Cyan Glow wapas lane ke liye
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #0b0e14; color: #00fbff; }
    h1 { color: #00fbff; font-family: 'Orbitron', sans-serif; text-align: center; font-size: 60px; text-shadow: 0 0 20px #00fbff; }
    
    /* Mic recorder ke boring button ko hamare style mein badalna */
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 100px !important;
        width: 180px !important;
        height: 180px !important;
        border: 8px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        font-size: 22px !important;
        box-shadow: 0 0 30px rgba(0, 251, 255, 0.4) !important;
        display: block;
        margin: 0 auto;
    }
    
    .status-text { text-align: center; color: #a0aec0; font-family: 'Arial'; margin-top: 20px; }
    .chat-box { background: #1a202c; padding: 20px; border-radius: 15px; border-left: 5px solid #00fbff; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.write("<h1>AURA</h1>", unsafe_allow_html=True)

# Mic Tool: Iska button ab CSS se hamare style mein dikhega
text = speech_to_text(
    start_prompt="TAP", 
    stop_prompt="LISTENING...", 
    language='en', 
    just_once=True, 
    key='aura_mic'
)

if text:
    st.markdown(f'<div class="chat-box"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    with st.spinner("Aura is thinking..."):
        response = aura.ask(text)
        st.markdown(f'<div class="chat-box"><b>Aura:</b> {response}</div>', unsafe_allow_html=True)
        aura.speak(response)
else:
    st.markdown('<p class="status-text">Tap the button and speak to Aura</p>', unsafe_allow_html=True)
