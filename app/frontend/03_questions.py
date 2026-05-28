import os
import uuid
import requests
import streamlit as st


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="🏠",
    layout="wide",
)


# -----------------------------
# BACKEND CONFIG
# -----------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))


# -----------------------------
# QUESTIONS
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
# HELPERS
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
        json={
            "session_id": st.session_state.session_id,
            "message": message,
        },
        timeout=REQUEST_TIMEOUT,
    )


def initialize_session():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "last_intent" not in st.session_state:
        st.session_state.last_intent = None

    if "last_sources" not in st.session_state:
        st.session_state.last_sources = []

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None


def clear_chat():
    st.session_state.messages = []
    st.session_state.last_intent = None
    st.session_state.last_sources = []
    st.session_state.pending_question = None


def extract_category_and_question(message):
    category = "Manual Query"
    question = message

    if message.startswith("Category:"):
        lines = message.split("\n")

        for line in lines:
            if line.startswith("Category:"):
                category = line.replace("Category:", "").strip()

            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()

    return category, question


def format_user_message(message):
    category, question = extract_category_and_question(message)

    if message.startswith("Category:"):
        return f"**Category:** {category}\n\n**Question:** {question}"

    return question


def format_assistant_message(category, question, answer):
    return (
        f"### Category\n{category}\n\n"
        f"### Question\n{question}\n\n"
        f"### Response\n{answer}"
    )


# -----------------------------
# INIT
# -----------------------------
initialize_session()


# -----------------------------
# SIDEBAR (Session + Intent + Sources)
# -----------------------------
with st.sidebar:

    st.header("🧾 Session")

    st.write("Session ID")
    st.code(st.session_state.session_id)

    st.markdown("### Intent")
    st.write(st.session_state.last_intent or "No intent yet")

    st.markdown("### Sources")
    if st.session_state.last_sources:
        st.json(st.session_state.last_sources)
    else:
        st.write("No sources available")

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat()
        st.rerun()


# -----------------------------
# HEADER
# -----------------------------
st.title("🏠 HomeShield Copilot")


# -----------------------------
# MAIN LAYOUT (CHAT ONLY)
# -----------------------------
st.subheader("💬 Chat")


# -----------------------------
# QUESTIONS UI
# -----------------------------
with st.expander("☰ Most Asked Questions", expanded=True):

    category = st.selectbox(
        "Select Category",
        list(QUESTION_MENU.keys())
    )

    questions = QUESTION_MENU[category]

    cols_per_row = 2

    for i in range(0, len(questions), cols_per_row):
        row = questions[i:i + cols_per_row]
        cols = st.columns(cols_per_row)

        for j, q in enumerate(row):
            with cols[j]:
                if st.button(q, key=f"q_{i}_{j}", use_container_width=True):
                    st.session_state.pending_question = build_question_message(
                        category,
                        q
                    )
                    st.rerun()

st.markdown("---")


# -----------------------------
# CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -----------------------------
# INPUT
# -----------------------------
user_input = st.chat_input("Ask your question...")

if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None


# -----------------------------
# PROCESS MESSAGE
# -----------------------------
if user_input:

    category, question = extract_category_and_question(user_input)

    user_display = format_user_message(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_display}
    )

    with st.chat_message("user"):
        st.markdown(user_display)

    with st.chat_message("assistant"):

        try:
            with st.spinner("Thinking..."):
                response = send_message_to_backend(user_input)

            if response.status_code != 200:
                answer = f"Error: {response.status_code}"
            else:
                data = parse_response_json(response)

                answer = data.get("answer", "No answer returned")

                # ✅ Store Sidebar Data
                st.session_state.last_intent = data.get("intent")
                st.session_state.last_sources = data.get("sources", [])

            assistant_msg = format_assistant_message(
                category,
                question,
                answer
            )

            st.markdown(assistant_msg)

            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_msg}
            )

        except Exception as e:
            st.error(str(e))

    st.rerun()