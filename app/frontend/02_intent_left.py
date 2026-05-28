import os
import uuid
import requests
import streamlit as st

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="🏠",
    layout="wide",
)

# -----------------------------
# Backend config
# -----------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

# -----------------------------
# Question menu
# -----------------------------
QUESTION_MENU = {
    "Coverage and Policy": [
        "What does home insurance cover?",
        "What is the buildings and contents cover limit in Standard policy?",
        "What is not covered in insurance policy?",
        "What is covered under Standard buildings insurance?",
        "What is contents limit?",
    ],
    "Claims and Scenarios": [
        "My pipe burst and damaged the ceiling. Is this covered?",
        "I had a water leak in my kitchen. Can I claim for repairs?",
        "Storm damaged my roof tiles. Will insurance cover it?",
        "Is theft covered if there was no forced entry?",
        "Storm blew my fence panel down. Is this covered?",
        "Is tenant malicious damage covered under my policy?",
        "Is wear and tear covered under my home insurance policy?",
    ],
}

# -----------------------------
# Helper functions
# -----------------------------
def build_question_message(category, question):
    return f"Category: {category}\nQuestion: {question}"


def parse_response_json(response):
    try:
        return response.json()
    except Exception:
        return {"detail": response.text}


def send_message_to_backend(message):
    return requests.post(
        f"{API_BASE_URL}/chat",
        json={"session_id": st.session_state.session_id, "message": message},
        timeout=REQUEST_TIMEOUT,
    )


def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_intent" not in st.session_state:
        st.session_state.last_intent = None

    if "last_memory" not in st.session_state:
        st.session_state.last_memory = {}

    if "last_sources" not in st.session_state:
        st.session_state.last_sources = []


# -----------------------------
# Init
# -----------------------------
initialize_session()

# -----------------------------
# UI Header
# -----------------------------
st.title("🏠 HomeShield Copilot")

# -----------------------------
# Layout
# -----------------------------
left_col, right_col = st.columns([2, 1])

# -----------------------------
# Chat section
# -----------------------------
with left_col:
    st.subheader("💬 Chat")

    # chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # question menu
    with st.expander("Questions"):
        category = st.selectbox("Category", list(QUESTION_MENU.keys()))
        for i, q in enumerate(QUESTION_MENU[category]):
            if st.button(q, key=f"q{i}"):
                st.session_state.pending_question = build_question_message(category, q)
                st.rerun()

    user_input = st.chat_input("Ask your question...")

    if "pending_question" in st.session_state:
        user_input = st.session_state.pending_question
        del st.session_state.pending_question

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Thinking..."):
                    response = send_message_to_backend(user_input)

                if response.status_code != 200:
                    st.error("Backend Error")
                else:
                    # ✅ FIXED BLOCK
                    data = parse_response_json(response)

                    answer = data.get("answer", "No answer returned.")

                    st.markdown(answer)

                    # debug handling
                    if data.get("intent") == "error" or data.get("error"):
                        st.error("Backend debug error detected")
                        st.code(str(data.get("error")))
                        st.code(str(data.get("traceback")))

                    # store state
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                    st.session_state.last_intent = data.get("intent")
                    st.session_state.last_memory = data.get("memory", {})
                    st.session_state.last_sources = data.get("sources", [])

            except Exception as e:
                st.error(f"Error: {str(e)}")

# -----------------------------
# Right panel
# -----------------------------
with right_col:
    st.subheader("Details")

    st.write("Intent")
    st.code(st.session_state.last_intent)

    st.write("Memory")
    st.json(st.session_state.last_memory)

    st.write("Sources")
    st.json(st.session_state.last_sources)
