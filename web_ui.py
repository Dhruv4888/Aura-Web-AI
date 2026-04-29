import streamlit as st
import time
from ai_engine import aura
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Gyan Setu AI", layout="centered")

# JavaScript for Smooth Audio Queueing (Parallel Processing)
def play_audio_js(b64_data):
    js_code = f"""
        <script>
            var audio = new Audio("data:audio/mp3;base64,{b64_data}");
            audio.play();
        </script>
    """
    st.components.v1.html(js_code, height=0)

st.markdown("<h1>GYAN SETU</h1>", unsafe_allow_html=True)

query_voice = speech_to_text(start_prompt="TAP TO SPEAK", language='en-IN', key='v12')

if query_voice:
    if "messages" not in st.session_state: st.session_state.messages = []
    st.markdown(f"**Student:** {query_voice}")
    
    full_text = ""
    current_sentence = ""
    ui_box = st.empty()
    
    # Starting the stream
    for fragment in aura.ask_stream(query_voice, st.session_state.messages):
        if fragment == "||SYNC||":
            if current_sentence.strip():
                # Get audio and play IMMEDIATELY via JS
                v_data = aura.get_audio_data(current_sentence.strip())
                if v_data:
                    play_audio_js(v_data)
                current_sentence = ""
        else:
            full_text += fragment
            current_sentence += fragment
            # Visual update doesn't wait for audio now
            ui_box.markdown(f"**Gyan Setu:** {full_text}▒")
            time.sleep(0.03) # Matching natural reading speed

    st.session_state.messages.append({"role": "user", "content": query_voice})
    st.session_state.messages.append({"role": "assistant", "content": full_text})
