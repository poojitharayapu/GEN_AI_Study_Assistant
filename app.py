import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.title("AI Study Assistant")

if not api_key:
    st.error("API key not found. Please check GEMINI_API_KEY in your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

question = st.text_input("Type your doubt here:")

if st.button("Ask") and question:
    with st.spinner("Thinking..."):
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="You are a study assistant. Answer in clear study notes with a short heading, key points as bullet points, one simple example, and a 3-line summary at the end. Topic: " + question,
        )
    st.write(response.text)