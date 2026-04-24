import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

# Page Config Update: Title change to Gyan Setu
st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# --- MEMORY INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# CSS: Wahi futuristic look par naye naam ke saath
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #0b0e14 !important; }
    
    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 50px !important; 
        text-shadow: 0 0 20px #00fbff;
        margin-top: -50px;
    }
    
    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 100px !important;
        width: 180px !important;
        height: 180px !important;
        border: 8px solid #1a202c !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: bold !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 0 30px rgba(0, 251, 255, 0.4) !important;
    }

    .chat-container {
        background: #1a202c;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00fbff;
        color: white;
        margin-top: 20px;
        font-family: 'Arial', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}
    </style>
    """, unsafe_allow_html=True)

# Main Title Change
st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

# Mic Tool
text = speech_to_text(
    start_prompt="TAP TO ASK", 
    stop_prompt="LISTENING...", 
    language='en-IN', 
    use_container_width=True,
    just_once=True, 
    key='gyansetu_mic'
)

if text:
    st.markdown(f'<div class="chat-container"><b>You:</b> {text}</div>', unsafe_allow_html=True)
    
    with st.spinner("Gyan Setu is thinking..."):
        # Gyan Setu se response maangna
        response = aura.ask(text, st.session_state.messages)
        
        st.session_state.messages.append({"role": "user", "content": text})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display as Gyan Setu
        st.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {response}</div>', unsafe_allow_html=True)
        aura.speak(response)
else:
    st.markdown('<p style="text-align:center; color:#555; margin-top:20px;">Ready for your questions...</p>', unsafe_allow_html=True)
