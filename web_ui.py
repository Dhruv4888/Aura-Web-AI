import streamlit as st
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text
import time
import base64
import re

st.set_page_config(page_title="Gyan Setu AI", page_icon="🎓", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Cosmic CSS (Kept same as your original)
st.markdown("""<style>...</style>""", unsafe_allow_html=True) # Paste your CSS here

st.write("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

def inject_isolated_audio(b64_data, chunk_id):
    # Unique ID for every audio bit to ensure no overlap
    audio_markup = f"""
        <div style="display:none;">
            <audio autoplay="true" id="aud_{chunk_id}">
                <source src="data:audio/mp3;base64,{b64_data}" type="audio/mp3">
            </audio>
        </div>
    """
    st.components.v1.html(audio_markup, height=0)

query_voice = speech_to_text(start_prompt="TAP TO SPEAK", language='en-IN', use_container_width=True, key='v12')

if query_voice:
    st.markdown(f'<div class="chat-container user-box"><b>Student:</b> {query_voice}</div>', unsafe_allow_html=True)
    
    full_transcription = ""
    chunk_buffer = ""
    ui_anchor = st.empty()
    audio_counter = 0
    
    # Text aur Voice ko ek saath chalane ka logic
    for text_fragment in aura.ask_stream(query_voice, st.session_state.messages):
        if text_fragment == "||SYNC_SIGNAL||":
            if chunk_buffer.strip():
                audio_counter += 1
                vocal_hex = aura.get_audio_data(chunk_buffer.strip())
                if vocal_hex:
                    inject_isolated_audio(vocal_hex, audio_counter)
                
                # Minimum wait to allow audio to start
                time.sleep(0.1) 
                chunk_buffer = "" 
        else:
            full_transcription += text_fragment
            chunk_buffer += text_fragment
            # Immediate UI Update
            ui_anchor.markdown(f'<div class="chat-container"><b>Gyan Setu:</b> {full_transcription}▒</div>', unsafe_allow_html=True)
            # Typewriter feel matching speech
            time.sleep(0.04)

    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_transcription})
