import uuid
import sys
import requests
import streamlit as st

sys.path.append('/home/ubuntu/homeshield-insurance-copilot_01/app')
#from app.config import settings
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


with st.sidebar:
    st.header("Session")
    st.code(st.session_state.session_id)

    if st.button("Clear chat"):
        st.session_state.messages = []
        try:
            requests.delete(f"{settings.API_BASE_URL}/memory/{st.session_state.session_id}")
        except Exception:
            pass
        st.rerun()

    st.header("Document Ingestion")
    if st.button("Run ingestion"):
        try:
            response = requests.post(f"{settings.API_BASE_URL}/ingest", timeout=60)
            st.success(response.json())
        except Exception as exc:
            st.error(f"Ingestion failed: {exc}")

    st.header("Demo Questions")
    st.markdown(
        """
        - What is covered under Standard buildings insurance?
        - Is accidental damage included in Standard?
        - Storm blew my fence down. Is it covered?
        - Estimate burst pipe internal ceiling damage for a 3-bed semi-detached house.
        - Track claim CLM12345.
        """
    )


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_message = st.chat_input("Ask about policy cover, exclusions, claims, or repair costs...")

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
            response = requests.post(
                f"{settings.API_BASE_URL}/chat",
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()

            st.markdown(data["answer"])

            with st.expander("Intent, Memory and Sources"):
                st.subheader("Intent")
                st.code(data["intent"])

                st.subheader("Memory")
                st.json(data["memory"])

                st.subheader("Sources")
                if data.get("sources"):
                    for source in data["sources"]:
                        st.markdown(
                            f"**{source['document']}** | "
                            f"Chunk `{source['chunk_id']}` | "
                            f"Score `{source['score']}`"
                        )
                        st.caption(source["text_preview"])
                else:
                    st.write("No sources returned.")

            assistant_message = data["answer"]

        except Exception as exc:
            assistant_message = f"Backend error: {exc}"
            st.error(assistant_message)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message,
        }
    )