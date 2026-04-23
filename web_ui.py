import streamlit as st
from ai_engine import aura

st.set_page_config(page_title="AURA AI", page_icon="🎙️")

# CSS for Aura Look
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #00fbff; }
    .stButton>button {
        background-color: #00fbff; color: black;
        border-radius: 80px; width: 160px; height: 160px;
        border: 10px solid #1a202c; font-family: 'Orbitron'; font-weight: bold;
        display: block; margin: auto;
    }
    h1 { color: #00fbff; font-family: 'Orbitron'; text-align: center; font-size: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.title("AURA")

if st.button("TAP"):
    query = aura.listen()
    if query:
        st.write(f"**You:** {query}")
        response = aura.ask(query)
        st.write(f"**Aura:** {response}")
        aura.speak(response)