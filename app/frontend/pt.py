"""import sys
sys.path.append('/home/ubuntu/homeshield-insurance-copilot/app')
#from app.config import settings
from config import settings

-----------------
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("OpenAI key is working.")
    print("First model:", models.data[0].id)
except Exception as e:
    print("OpenAI key test failed.")
    print(e)
"""
import uuid
import sys
import requests
import streamlit as st

sys.path.append('/home/ubuntu/homeshield-insurance-copilot_01/app')
from config import settings


st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 HomeShield Property Insurance Copilot")
st.caption("Capstone project: Agentic RAG + memory + tools + guardrails")


if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4()}"

if "messages" not in st.session_state:
    st.session_state.messages = []


user_message = None


with st.sidebar:
    st.header("Session")
    st.code(st.session_state.session_id)

    if st.button("Clear chat"):
        st.session_state.messages = []
        try:
            requests.delete(
                f"{settings.API_BASE_URL}/memory/{st.session_state.session_id}"
            )
        except Exception:
            pass
        st.rerun()

    st.header("Document Ingestion")

    if st.button("Run ingestion"):
        try:
            response = requests.post(
                f"{settings.API_BASE_URL}/ingest",
                timeout=60
            )
            response.raise_for_status()
            st.success(response.json())
        except Exception as exc:
            st.error(f"Ingestion failed: {exc}")

    st.header("Explore Questions")

    category = st.selectbox(
        "Select Category",
        [
            "Coverage and Policy",
            "Claims and Scenarios",
            "Repairs and Costs",
            "Policy Features",
            "Claim Tracking"
        ]
    )

    if category == "Coverage and Policy":
        if st.button("What does my home insurance cover?"):
            user_message = "What does my home insurance cover?"

        if st.button("What are the buildings and contents limits?"):
            user_message = "What is the buildings and contents cover limit in Standard policy?"

        if st.button("What is not covered in my policy?"):
            user_message = "What is not covered in my insurance policy?"

    elif category == "Claims and Scenarios":
        if st.button("Pipe burst — is it covered?"):
            user_message = "My pipe burst and damaged the ceiling — is this covered?"

        if st.button("Kitchen water leak claim"):
            user_message = "I had a water leak in my kitchen — can I claim for repairs?"

        if st.button("Storm roof damage"):
            user_message = "Storm damaged my roof tiles — will insurance cover it?"

        if st.button("Theft without forced entry"):
            user_message = "Is theft covered if there was no forced entry?"

    elif category == "Repairs and Costs":
        if st.button("Water damage repair cost"):
            user_message = "How much does it cost to repair water damage in a 3-bed house?"

        if st.button("Roof repair estimate"):
            user_message = "Estimate cost for roof repair after storm damage"

        if st.button("Do I need multiple quotes?"):
            user_message = "Do I need multiple quotes for claim approval?"

    elif category == "Policy Features":
        if st.button("Is accidental damage included?"):
            user_message = "Is accidental damage included in my policy?"

        if st.button("What is the claim excess?"):
            user_message = "What is the claim excess amount?"

        if st.button("Can I upgrade policy?"):
            user_message = "Can I upgrade from Standard to Comprehensive?"

    elif category == "Claim Tracking":
        if st.button("Track claim status"):
            user_message = "Track claim "

        if st.button("Documents required"):
            user_message = "What documents are required for a claim?"


# Display chat history in main page, not sidebar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


chat_input = st.chat_input(
    "Ask about policy cover, exclusions, claims, or repair costs..."
)

if chat_input:
    user_message = chat_input


if user_message:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_message,
    }

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{settings.API_BASE_URL}/chat",
                    json=payload,
                    timeout=60,
                )

                response.raise_for_status()
                data = response.json()

            answer = data.get("answer")

            if answer:
                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
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
                            st.markdown(
                                f"**{source.get('document', '')}** "
                                f"Chunk `{source.get('chunk_id', '')}` "
                                f"Score `{source.get('score', '')}`"
                            )
                            st.caption(source.get("text_preview", ""))
                    else:
                        st.write("No sources returned.")

            else:
                st.error("Backend response does not contain 'answer'.")
                st.json(data)

        except Exception as exc:
            error_message = f"Backend error: {exc}"
            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )
