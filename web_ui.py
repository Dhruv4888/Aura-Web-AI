import streamlit as st
import time

# Pehle import ko safe banate hain
try:
    from ai_engine import aura
except ImportError as e:
    st.error(f"File Connection Error: {e}. Please ensure 'ai_engine.py' is in the same folder.")
    st.stop()

from streamlit_mic_recorder import speech_to_text

# --- UI Layout (Aapka original style) ---
st.set_page_config(page_title="Gyan Setu AI", layout="centered")

# CSS aur Title (Wahi purana layout)
st.markdown("<style>/* Aapka Cosmic CSS yahan */</style>", unsafe_allow_html=True)
st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def play_audio(b64_data, count):
    html_code = f"""<audio autoplay="true" id="aud_{count}"><source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3"></audio>"""
    st.components.v1.html(html_code, height=0)

query_voice = speech_to_text(start_prompt="TAP TO SPEAK", language='en-IN', key='v12')

if query_voice:
    if "messages" not in st.session_state: st.session_state.messages = []
    st.markdown(f'<div style="color:white; background:rgba(255,255,255,0.1); padding:20px; border-radius:15px;"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    full_transcription = ""
    sentence_buffer = ""
    ui_anchor = st.empty()
    audio_id = 0
    
    # Real-time Streaming logic
    for fragment in aura.ask_stream(query_voice, st.session_state.messages):
        if fragment == "||SYNC_SIGNAL||":
            if sentence_buffer.strip():
                audio_id += 1
                vocal_data = aura.get_audio_data(sentence_buffer.strip())
                if vocal_data:
                    play_audio(vocal_data, audio_id)
                sentence_buffer = ""
        else:
            full_transcription += fragment
            sentence_buffer += fragment
            ui_anchor.markdown(f'<div style="color:#00fbff; background:black; padding:30px; border-radius:20px; border-left:10px solid #00fbff;"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
            time.sleep(0.02)

    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_transcription})
