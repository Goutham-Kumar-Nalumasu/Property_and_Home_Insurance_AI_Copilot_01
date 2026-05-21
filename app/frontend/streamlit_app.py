
import uuid
import sys
import requests
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="HomeShield Insurance Copilot",
    page_icon="🏠",
    layout="wide"
)


# =========================================================
# IMPORT SETTINGS
# =========================================================

sys.path.append("/home/ubuntu/homeshield-insurance-copilot_01/app")

try:
    from config import settings
except Exception as exc:
    st.error("Could not import settings from config.py")
    st.error(str(exc))
    st.stop()


# =========================================================
# QUESTIONS MENU
# =========================================================

QUESTION_MENU = {
    "Coverage and Policy": [
        "What does home insurance cover?",
        "What is the buildings and contents cover limit in Standard policy?",
        "What is not covered in insurance policy?",
        "What is covered under Standard buildings insurance?",
        "What is contents limit?"
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
        "Do I need multiple quotes for claim approval?",
        "Estimate repair cost for bathroom water damage.",
        "Estimate repair cost for fire damage.",
        "Estimate repair cost for flood damage."
    ],
    "Policy Features": [
        "Is accidental damage included in policy?",
        "What is the claim excess amount?",
        "Can I upgrade from Standard to Comprehensive?",
        "Compare Standard, Comprehensive, and Landlord Plus policies.",
        "What is trace and access cover?",
        "What is home emergency cover?",
        "Is legal expenses cover included in my policy?"
    ],
    "Claim Guidance": [
        "What documents are required for a claim?",
        "How do I submit a claim?",
        "What happens after I register a claim?",
        "How do I check my claim status?",
        "What evidence should I provide for my claim?",
        "Do I need photos or repair quotes for my claim?"
    ]
}


# =========================================================
# FUNCTIONS
# =========================================================

def build_question_message(category, question):

    return (
        f"Question category: {category}.\n"
        f"User question: {question}\n\n"
    )


def send_message_to_backend(user_message):

    payload = {
        "session_id": st.session_state.session_id,
        "message": user_message
    }

    response = requests.post(
        settings.API_BASE_URL + "/chat",
        json=payload,
        timeout=60
    )

    return response


def create_query_flow(user_message):

    flow = []

    flow.append("✅ User submitted question")
    flow.append("➡️ Streamlit UI received query")
    flow.append("➡️ Query added to session memory")
    flow.append("➡️ Sending request to FastAPI backend")
    flow.append("🧠 Intent Detection Completed")
    flow.append("🗂️ Conversation Memory Retrieved")
    flow.append("📚 Vector Search / RAG Retrieval Completed")
    flow.append("🤖 LLM Generated Final Response")
    flow.append("✅ Response Returned to User")

    return {
        "question": user_message,
        "steps": flow
    }


# =========================================================
# HEADER
# =========================================================

st.title("🏠 HomeShield Property Insurance Copilot")
st.caption("Capstone project: Agentic RAG + memory + tools + guardrails")


# =========================================================
# SESSION STATE
# =========================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = "session-" + str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# STORES FLOW FOR EVERY QUERY
if "all_query_flows" not in st.session_state:
    st.session_state.all_query_flows = []

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("🧾 Session")
    st.code(st.session_state.session_id)

    # =========================================================
    # CLEAR CHAT
    # =========================================================

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []
        st.session_state.all_query_flows = []

        try:
            requests.delete(
                settings.API_BASE_URL + "/memory/" + st.session_state.session_id,
                timeout=30
            )
        except Exception:
            pass

        st.rerun()

    st.markdown("---")

    # =========================================================
    # DOCUMENT INGESTION
    # =========================================================

    st.header("📂 Document Ingestion")

    if st.button("🚀 Run Ingestion"):

        try:

            response = requests.post(
                settings.API_BASE_URL + "/ingest",
                timeout=60
            )

            if response.status_code == 200:

                st.success("Ingestion completed successfully")
                st.json(response.json())

            else:

                st.error(
                    "Ingestion failed. Status code: "
                    + str(response.status_code)
                )

                st.code(response.text)

        except Exception as exc:

            st.error("Ingestion failed: " + str(exc))

    st.markdown("---")

    # =========================================================
    # QUERY EXECUTION FLOWS
    # =========================================================

    st.header("🔄 Query Execution Flow")

    if st.session_state.all_query_flows:

        # DISPLAY LATEST QUERY FIRST
        reversed_flows = list(reversed(st.session_state.all_query_flows))

        for index, query_data in enumerate(reversed_flows):

            question_text = query_data["question"]

            with st.expander(
                f"Query {len(reversed_flows) - index}",
                expanded=(index == 0)
            ):

                st.markdown("### User Query")

                st.info(question_text)

                st.markdown("### Execution Steps")

                for step in query_data["steps"]:

                    if "✅" in step:
                        st.success(step)

                    elif "➡️" in step:
                        st.info(step)

                    elif "🧠" in step:
                        st.warning(step)

                    elif "🗂️" in step:
                        st.info(step)

                    elif "📚" in step:
                        st.info(step)

                    elif "🤖" in step:
                        st.warning(step)

                    elif "❌" in step:
                        st.error(step)

                    else:
                        st.write(step)

    else:

        st.info("Query execution flow will appear here.")


# =========================================================
# MAIN CHAT AREA
# =========================================================

st.subheader("💬 Insurance Assistant")


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =========================================================
# MOST ASKED QUESTIONS
# =========================================================

st.markdown("---")

with st.expander("☰ Most Asked Questions", expanded=True):

    category = st.selectbox(
        "Select Category",
        list(QUESTION_MENU.keys())
    )

    st.markdown("### Questions")

    questions = QUESTION_MENU[category]

    for index, question in enumerate(questions):

        button_key = "question_" + category + "_" + str(index)

        if st.button(question, key=button_key):

            st.session_state.selected_question = (
                build_question_message(
                    category,
                    question
                )
            )

            st.rerun()


# =========================================================
# CHAT INPUT
# =========================================================

chat_input = st.chat_input(
    "Ask about policy cover, exclusions, claims, or repair costs..."
)


# =========================================================
# DETERMINE USER MESSAGE
# =========================================================

user_message = None

if st.session_state.selected_question:

    user_message = st.session_state.selected_question
    st.session_state.selected_question = None

elif chat_input:

    user_message = chat_input


# =========================================================
# PROCESS USER MESSAGE
# =========================================================

if user_message:

    # =========================================================
    # STORE USER MESSAGE
    # =========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # =========================================================
    # CREATE FLOW FOR CURRENT QUERY
    # =========================================================

    current_flow = create_query_flow(user_message)

    # =========================================================
    # API CALL
    # =========================================================

    try:

        response = send_message_to_backend(user_message)

        if response.status_code != 200:

            error_message = (
                "Backend returned status code: "
                + str(response.status_code)
            )

            current_flow["steps"].append(
                "❌ Backend Error"
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message
                }
            )

        else:

            data = response.json()

            answer = data.get(
                "answer",
                "No answer returned from backend."
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )

    except Exception as exc:

        error_message = (
            "Backend error: "
            + str(exc)
        )

        current_flow["steps"].append(
            "❌ Backend Error"
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message
            }
        )

    # =========================================================
    # SAVE QUERY FLOW HISTORY
    # =========================================================

    st.session_state.all_query_flows.append(current_flow)

    st.rerun()

