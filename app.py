import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from pypdf import PdfReader

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.title("AI Study Assistant")

if not api_key:
    st.error("API key not found. Please check GEMINI_API_KEY in your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"

if "history" not in st.session_state:
    st.session_state.history = []


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


tab1, tab2, tab3, tab4 = st.tabs(["Study Notes", "Quiz", "PDF Q&A", "Study Plan"])

with tab1:
    question = st.text_input("Type your doubt here:")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            answer = ask_gemini(
                "You are a study assistant. Answer in clear study notes with a short heading, "
                "key points as bullet points, one simple example, and a 3-line summary at the end. "
                "Topic: " + question
            )
        st.session_state.history.append((question, answer))
        st.write(answer)

    if st.session_state.history:
        st.divider()
        st.subheader("History")
        for q, a in reversed(st.session_state.history):
            with st.expander(q):
                st.write(a)
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()

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

with tab3:
    pdf_file = st.file_uploader("Upload a PDF", type="pdf")
    pdf_question = st.text_input("Ask a question about the PDF:")
    if st.button("Ask PDF") and pdf_file and pdf_question:
        with st.spinner("Reading PDF..."):
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            text = text[:30000]
        if not text.strip():
            st.error("Could not read any text from this PDF.")
        else:
            with st.spinner("Thinking..."):
                pdf_answer = ask_gemini(
                    "Answer the question using only the PDF content below. "
                    "If the answer is not in the PDF, say so.\n\n"
                    "PDF content:\n" + text + "\n\nQuestion: " + pdf_question
                )
            st.write(pdf_answer)

with tab4:
    course = st.text_input("What course do you want to learn?")
    weeks = st.number_input("How many weeks?", min_value=1, max_value=52, value=4)
    hours = st.number_input("Hours per day?", min_value=1, max_value=12, value=2)
    if st.button("Create Plan") and course:
        with st.spinner("Creating your study plan..."):
            plan = ask_gemini(
                "Create a week-by-week study plan for learning the course below. "
                "For each week give a theme, daily topics, practice tasks, and a mini goal. "
                "End with tips and a list of free resources. "
                "Course: " + course + ". Duration: " + str(weeks) + " weeks. "
                "Study time: " + str(hours) + " hours per day."
            )
        st.write(plan)