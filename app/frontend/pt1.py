import uuid
import sys
import requests
import streamlit as st


# Page config
st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="home",
    layout="wide"
)


# Import settings
sys.path.append("/home/ubuntu/homeshield-insurance-copilot_01/app")

try:
    from config import settings
except Exception as exc:
    st.error("Could not import settings from config.py")
    st.error(str(exc))
    st.stop()


QUESTION_MENU = {
    "Coverage and Policy": [
        "What does my home insurance cover?",
        "What is the buildings and contents cover limit in Standard policy?",
        "What is not covered in my insurance policy?",
        "What is covered under Standard buildings insurance?",
        "What is my contents limit?"
    ],

    "Claims and Scenarios": [
        "My pipe burst and damaged the ceiling. Is this covered?",
        "I had a water leak in my kitchen. Can I claim for repairs?",
        "Storm damaged my roof tiles. Will insurance cover it?",
        "Is theft covered if there was no forced entry?",
        "Storm blew my fence panel down. Is this covered?",
        "Is tenant malicious damage covered under my policy?",
        "Is wear and tear covered under my home insurance policy?"
    ],

    "Repairs and Costs": [
        "How much does it cost to repair water damage in a 3-bed house?",
        "Estimate repair cost for burst pipe internal ceiling damage for a 3-bed semi-detached house.",
        "Estimate cost for roof repair after storm damage.",
        "Do I need multiple quotes for repairs?",
        "Estimate repair cost for bathroom water damage.",
        "Estimate repair cost for fire damage.",
        "Estimate repair cost for flood damage."
    ],

    "Policy Features": [
        "Is accidental damage included in my policy?",
        "What is the claim excess amount?",
        "Can I upgrade from Standard to Comprehensive?",
        "Compare Standard, Comprehensive, and Landlord Plus policies.",
        "What is trace and access cover?",
        "What is home emergency cover?",
        "Is legal expenses cover included in my policy?"
    ],

    "Claim Tracking": [
        "What documents are required when making a claim?",
        "How do I submit a home insurance claim?",
        "What happens after I register a claim?",
        "What evidence should I provide for my claim?",
        "Do I need photos or repair quotes when filing a claim?"
    ]
}


# Header
st.title("HomeShield Property Insurance Copilot")
st.caption("Capstone project: Agentic RAG + memory + tools + guardrails")


# Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = "session-" + str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []


user_message = None


# Sidebar
with st.sidebar:
    st.header("Session")
    st.code(st.session_state.session_id)

    if st.button("Clear chat"):
        st.session_state.messages = []

        try:
            requests.delete(
                settings.API_BASE_URL + "/memory/" + st.session_state.session_id,
                timeout=30
            )
        except Exception:
            pass

        st.rerun()

    st.header("Document Ingestion")

    if st.button("Run ingestion"):
        try:
            response = requests.post(
                settings.API_BASE_URL + "/ingest",
                timeout=60
            )

            if response.status_code == 200:
                st.success(response.json())
            else:
                st.error("Ingestion failed. Status code: " + str(response.status_code))
                st.code(response.text)

        except Exception as exc:
            st.error("Ingestion failed: " + str(exc))

    st.header("Explore Questions")

    category = st.selectbox(
        "Select Category",
        list(QUESTION_MENU.keys())
    )

    st.markdown("### Questions")

    questions = QUESTION_MENU[category]

    for index, question in enumerate(questions):
        button_key = category + "_" + str(index)

        if st.button(question, key=button_key):
            user_message = question


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Manual chat input
chat_input = st.chat_input(
    "Ask about policy cover, exclusions, claims, or repair costs..."
)

if chat_input:
    user_message = chat_input


# Process user message
if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_message
    }

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    settings.API_BASE_URL + "/chat",
                    json=payload,
                    timeout=60
                )

            if response.status_code != 200:
                error_message = "Backend returned status code: " + str(response.status_code)

                st.error(error_message)
                st.code(response.text)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message + "\n\n" + response.text
                    }
                )

            else:
                data = response.json()
                answer = data.get("answer", "No answer returned from backend.")

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                with st.expander("Intent, Memory and Sources"):
                    st.subheader("Intent")
                    st.code(data.get("intent", "No intent returned"))

                    st.subheader("Memory")
                    st.json(data.get("memory", {}))

                    st.subheader("Sources")
                    sources = data.get("sources", [])

                    if sources:
                        for source in sources:
                            document = source.get("document", "")
                            chunk_id = str(source.get("chunk_id", ""))
                            score = str(source.get("score", ""))

                            st.markdown(
                                "**" + document + "** "
                                "Chunk `" + chunk_id + "` "
                                "Score `" + score + "`"
                            )

                            st.caption(source.get("text_preview", ""))
                    else:
                        st.write("No sources returned.")

        except Exception as exc:
            error_message = "Backend error: " + str(exc)

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )