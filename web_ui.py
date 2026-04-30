# web_ui.py
import streamlit as st
from streamlit_mic_recorder import speech_to_text
from ai_engine import aura
import base64
import time
import json


if "messages" not in st.session_state:
    st.session_state.messages = []


st.set_page_config(
    page_title="Gyan Setu AI - Global Academic Mentor",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# --- UI Style (same cosmic orbitron)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;600;700&display=swap');
    
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%) !important; }

    h1 { 
        color: #00fbff !important; 
        font-family: 'Orbitron', sans-serif !important; 
        text-align: center !important; 
        font-size: 65px !important; 
        text-shadow: 0 0 40px #00fbff, 0 0 15px rgba(0, 251, 255, 0.5);
        margin-top: -85px;
        letter-spacing: 12px;
        text-transform: uppercase;
        font-weight: 900;
    }

    button[data-testid="stBaseButton-secondary"] {
        background-color: #00fbff !important;
        color: #0b0e14 !important;
        border-radius: 50% !important;
        width: 175px !important;
        height: 175px !important;
        border: 15px solid #1e293b !important;
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 900 !important;
        margin: 45px auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 0 70px rgba(0, 251, 255, 0.35) !important;
        transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        cursor: pointer;
    }

    button[data-testid="stBaseButton-secondary"]:hover {
        transform: scale(1.1) rotate(-2deg);
        box-shadow: 0 0 100px rgba(0, 251, 255, 0.8) !important;
        border-color: #ffffff !important;
    }

    .chat-container {
        background: rgba(15, 23, 42, 0.95);
        padding: 50px;
        border-radius: 35px;
        border-left: 20px solid #00fbff;
        color: #f1f5f9;
        margin-top: 40px;
        font-family: 'Rajdhani', sans-serif;
        line-height: 2.1;
        font-size: 28px;
        box-shadow: 30px 30px 80px rgba(0,0,0,0.85);
        border-right: 2px solid rgba(0, 251, 255, 0.1);
        backdrop-filter: blur(25px);
    }

    .user-box { 
        border-left: 20px solid #ffffff; 
        background: rgba(30, 41, 59, 0.95); 
        box-shadow: 15px 15px 50px rgba(0,0,0,0.6);
    }

    #MainMenu, header, footer {visibility: hidden;}
    div[data-testid="stDecoration"] {display:none;}

    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { 
        background: linear-gradient(#00fbff, #005f61); 
        border-radius: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)


# Text + audio stream handler (NOT word‑by‑word sync, but NO OVERLAP)
query_voice = speech_to_text(
    start_prompt="TAP TO SPEAK",
    stop_prompt="GYAN SETU IS PROCESSING...",
    language='en-IN',
    use_container_width=True,
    just_once=True,
    key='core_engine_v12_final'
)

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)

    with st.spinner("Synthesizing solution..."):
        full_text = ""
        ui_anchor = st.empty()

        # 1) TEXT STREAMING (typing effect)
        for text_fragment in aura.ask_stream(query_voice, st.session_state.messages):
            if text_fragment == "||SYNC_SIGNAL||":
                continue
            full_text += text_fragment
            ui_anchor.markdown(
                f'<div class="chat-container"><b>Gyan Setu:</b> {full_text}▒</div>',
                unsafe_allow_html=True,
            )

        ui_anchor.markdown(
            f'<div class="chat-container"><b>Gyan Setu:</b> {full_text}</div>',
            unsafe_allow_html=True,
        )

        # 2) SINGLE AUDIO PLAY (Madhur / Prabhat voice, only once)
        if full_text.strip():
            audio_hex = aura.get_audio_data(full_text)
            if audio_hex:
                # Fixed: autoplay audio without JS problems
                st.markdown(
                    f"""
                    <div style="display:none;">
                        <audio id="final_audio" autoplay="true">
                            <source src="data:audio/mp3;base64,{audio_hex}" type="audio/mp3">
                        </audio>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.session_state.messages.append({"role": "user", "content": query_voice})
        st.session_state.messages.append({"role": "assistant", "content": full_text})

else:
    st.markdown("""
        <div style="text-align:center; padding:60px;">
            <div style="color:#00fbff; font-family:Orbitron; letter-spacing:5px; font-weight:900; font-size:22px; text-shadow: 0 0 15px rgba(0, 251, 255, 0.4);">
                SYSTEM ONLINE: GYAN SETU
            </div>
        </div>
    """, unsafe_allow_html=True)
