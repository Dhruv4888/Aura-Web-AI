import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64

st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

# Aapka Original Cosmic CSS yahan aayega (UI change nahi kiya)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) 

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def play_audio(b64_data, count):
    html_code = f"""
        <audio autoplay="true" id="aud_{count}">
            <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
        </audio>
    """
    st.components.v1.html(html_code, height=0)

query_voice = speech_to_text(start_prompt="TAP TO SPEAK", language='en-IN', key='v12')

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    full_transcription = ""
    sentence_buffer = ""
    ui_anchor = st.empty()
    audio_id = 0
    
    # Ye hai asli parallel logic
    for fragment in aura.ask_stream(query_voice, st.session_state.get('messages', [])):
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
            # Bina kisi bhari sleep ke text print karna
            ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
            time.sleep(0.02) # Typing speed control

    # Save to history
    if "messages" not in st.session_state: st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_transcription})
