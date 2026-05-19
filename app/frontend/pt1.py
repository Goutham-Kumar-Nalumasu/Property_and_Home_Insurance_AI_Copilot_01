import uuid
import sys
import requests
import streamlit as st


# --------------------------------------------------
# Import settings
# --------------------------------------------------
# Update this path if your project folder is different
sys.path.append("/home/ubuntu/homeshield-insurance-copilot_01/app")

try:
    from config import settings
except Exception as exc:
    st.error(f"Could not import settings from config.py: {exc}")
    st.stop()


# --------------------------------------------------
# Demo Claim ID to Policy Mapping
# --------------------------------------------------
# Since there is no real claims database in this capstone project,
# this mapping is used for demo purpose.
CLAIM_POLICY_MAP = {
    "CLM12345": {
        "policy_type": "Standard",
        "property_size": "3-bed semi-detached house",
        "damage_type": "burst pipe",
    },
    "CLMWATER01": {
        "policy_type": "Standard",
        "property_size": "3-bed semi-detached house",
        "damage_type": "water damage",
    },
    "CLMSTORM01": {
        "policy_type": "Comprehensive",
        "property_size": "4-bed detached house",
        "damage_type": "storm damage",
    },
    "CLMFIRE01": {
        "policy_type": "Comprehensive",
        "property_size": "3-bed detached house",
        "damage_type": "fire damage",
    },
    "CLMTHEFT01": {
        "policy_type": "Standard",
        "property_size": "2-bed terraced house",
        "damage_type": "theft",
    },
    "CLMTENANT01": {
        "policy_type": "Landlord Plus",
        "property_size": "3-bed semi-detached house",
        "damage_type": "tenant malicious damage",
    },
}


def build_claim_context_message(claim_id, question):
    """
    Builds a detailed user message using claim context.
    This helps backend understand policy type, property size, and damage type.
    """
    claim_id = claim_id.strip().upper()
    claim_info = CLAIM_POLICY_MAP.get(claim_id)

    if claim_info:
        return (
            f"My claim ID is {claim_id}. "
            f"My policy type is {claim_info['policy_type']}. "
            f"My property size is {claim_info['property_size']}. "
            f"My claim/damage type is {claim_info['damage_type']}. "
            f"{question}"
        )

    return f"My claim ID is {claim_id}. {question}"


# --------------------------------------------------
# Streamlit Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 HomeShield Property Insurance Copilot")
st.caption("Capstone project: Agentic RAG + memory + tools + guardrails")


# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session-{uuid.uuid4()}"

if "messages" not in st.session_state:
    st.session_state.messages = []


# This variable is used by sidebar buttons and manual chat input
user_message = None


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.header("Session")
    st.code(st.session_state.session_id)

    if st.button("Clear chat"):
        st.session_state.messages = []

        try:
            requests.delete(
                f"{settings.API_BASE_URL}/memory/{st.session_state.session_id}",
                timeout=30,
            )
        except Exception:
            pass

        st.rerun()

    st.header("Document Ingestion")

    if st.button("Run ingestion"):
        try:
            response = requests.post(
                f"{settings.API_BASE_URL}/ingest",
                timeout=60,
            )

            if response.status_code == 200:
                st.success(response.json())
            else:
                st.error(f"Ingestion failed. Status code: {response.status_code}")
                st.code(response.text)

        except Exception as exc:
            st.error(f"Ingestion failed: {exc}")

    st.header("Explore Questions")

    claim_id_input = st.text_input(
        "Enter Claim ID",
        placeholder="Example: CLMWATER01",
    )

    claim_id_clean = claim_id_input.strip().upper()

    if claim_id_clean:
        claim_info = CLAIM_POLICY_MAP.get(claim_id_clean)

        if claim_info:
            st.success(f"Claim found: {claim_id_clean}")
            st.write(f"Policy Type: {claim_info['policy_type']}")
            st.write(f"Property Size: {claim_info['property_size']}")
            st.write(f"Damage Type: {claim_info['damage_type']}")
        else:
            st.warning(
                "Claim ID not found in demo mapping. "
                "Copilot will still answer using the entered claim ID."
            )

    category = st.selectbox(
        "Select Category",
        [
            "Coverage and Policy",
            "Claims and Scenarios",
            "Repairs and Costs",
            "Policy Features",
            "Claim Tracking",
        ],
    )

    if not claim_id_clean:
        st.info("Please enter a Claim ID first to get claim-based answers.")

    else:
        # --------------------------------------------------
        # Coverage and Policy
        # --------------------------------------------------
        if category == "Coverage and Policy":
            if st.button("What does my home insurance cover?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What does my home insurance cover?",
                )

            if st.button("Buildings and contents cover limit"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is the buildings and contents cover limit in my policy?",
                )

            if st.button("What is not covered?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is not covered in my insurance policy?",
                )

            if st.button("Standard buildings insurance cover"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is covered under Standard buildings insurance?",
                )

            if st.button("What is my contents limit?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is my contents limit?",
                )

        # --------------------------------------------------
        # Claims and Scenarios
        # --------------------------------------------------
        elif category == "Claims and Scenarios":
            if st.button("Pipe burst and ceiling damage"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "My pipe burst and damaged the ceiling — is this covered?",
                )

            if st.button("Kitchen water leak claim"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "I had a water leak in my kitchen — can I claim for repairs?",
                )

            if st.button("Storm roof damage"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Storm damaged my roof tiles — will insurance cover it?",
                )

            if st.button("Theft without forced entry"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Is theft covered if there was no forced entry?",
                )

            if st.button("Storm damaged my fence"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Storm blew my fence panel down. Is this covered?",
                )

            if st.button("Tenant malicious damage"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Is tenant malicious damage covered under my policy?",
                )

            if st.button("Wear and tear damage"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Is wear and tear covered under my home insurance policy?",
                )

        # --------------------------------------------------
        # Repairs and Costs
        # --------------------------------------------------
        elif category == "Repairs and Costs":
            if st.button("Water damage repair cost"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "How much does it cost to repair water damage?",
                )

            if st.button("Burst pipe ceiling repair estimate"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Estimate repair cost for burst pipe internal ceiling damage.",
                )

            if st.button("Roof repair estimate"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Estimate cost for roof repair after storm damage.",
                )

            if st.button("Multiple repair quotes"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Do I need multiple quotes for claim approval?",
                )

            if st.button("Bathroom water damage estimate"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Estimate repair cost for bathroom water damage.",
                )

            if st.button("Fire damage repair estimate"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Estimate repair cost for fire damage.",
                )

            if st.button("Flood damage repair estimate"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Estimate repair cost for flood damage.",
                )

        # --------------------------------------------------
        # Policy Features
        # --------------------------------------------------
        elif category == "Policy Features":
            if st.button("Is accidental damage included?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Is accidental damage included in my policy?",
                )

            if st.button("What is the claim excess?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is the claim excess amount?",
                )

            if st.button("Can I upgrade my policy?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Can I upgrade my policy?",
                )

            if st.button("Compare policies"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Compare Standard, Comprehensive, and Landlord Plus policies.",
                )

            if st.button("What is trace and access cover?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is trace and access cover?",
                )

            if st.button("What is home emergency cover?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What is home emergency cover?",
                )

            if st.button("Is legal expenses cover included?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Is legal expenses cover included in my policy?",
                )

        # --------------------------------------------------
        # Claim Tracking
        # --------------------------------------------------
        elif category == "Claim Tracking":
            if st.button("Track My Claim"):
                user_message = f"Track claim {claim_id_clean}"

            if st.button("What documents are required for a claim?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What documents are required for a claim?",
                )

            if st.button("How do I submit a claim?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "How do I submit a claim?",
                )

            if st.button("What happens after I register a claim?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What happens after I register a claim?",
                )

            if st.button("How do I check my claim status?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "How do I check my claim status?",
                )

            if st.button("What evidence should I provide?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "What evidence should I provide for my claim?",
                )

            if st.button("Do I need photos or repair quotes?"):
                user_message = build_claim_context_message(
                    claim_id_clean,
                    "Do I need photos or repair quotes for my claim?",
                )


# --------------------------------------------------
# Display Previous Chat Messages
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# Manual Chat Input
# --------------------------------------------------
chat_input = st.chat_input(
    "Ask about policy cover, exclusions, claims, or repair costs..."
)

if chat_input:
    user_message = chat_input


# --------------------------------------------------
# Process User Message
# --------------------------------------------------
if user_message:
    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_message)

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_message,
    }

    # Call backend
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{settings.API_BASE_URL}/chat",
                    json=payload,
                    timeout=60,
                )

            if response.status_code != 200:
                error_message = (
                    f"Backend returned status code: {response.status_code}"
                )

                st.error(error_message)
                st.code(response.text)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"{error_message}\n\n{response.text}",
                    }
                )

            else:
                data = response.json()

                answer = data.get(
                    "answer",
                    "No answer returned from backend.",
                )

                st.markdown(answer)

                # Save assistant message
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                # Show details
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

        except Exception as exc:
            error_message = f"Backend error: {exc}"

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                }
            )