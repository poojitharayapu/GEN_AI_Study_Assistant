import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.title("AI Study Assistant")

if not api_key:
    st.error("API key not found. Please check GEMINI_API_KEY in your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"


def ask_gemini(prompt, retries=4):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except errors.ServerError:
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                return "The server is busy right now. Please try again in a minute."


tab1, tab2 = st.tabs(["Study Notes", "Quiz"])

with tab1:
    question = st.text_input("Type your doubt here:")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            answer = ask_gemini(
                "You are a study assistant. Answer in clear study notes with a short heading, "
                "key points as bullet points, one simple example, and a 3-line summary at the end. "
                "Topic: " + question
            )
        st.write(answer)

with tab2:
    topic = st.text_input("Enter a topic for the quiz:")
    if st.button("Generate Quiz") and topic:
        with st.spinner("Creating quiz..."):
            quiz = ask_gemini(
                "Create a 5-question multiple choice quiz on the topic below. "
                "Give 4 options (A, B, C, D) for each question. "
                "Put all the correct answers at the very end under the heading 'Answers'. "
                "Topic: " + topic
            )
        st.write(quiz)