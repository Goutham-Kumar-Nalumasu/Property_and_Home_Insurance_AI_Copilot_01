# Property & Home Insurance AI Copilot

## Overview

The Property & Home Insurance AI Copilot is a production-grade Agentic RAG application designed to assist homeowners, claims handlers, and insurance support teams throughout the property insurance lifecycle.

The system combines:

* Agentic RAG
* Persistent Conversational Memory
* Multi-tool Dispatch
* FastAPI Backend
* Streamlit Frontend
* FAISS Vector Search
* LangChain Orchestration

The AI copilot supports:

* Policy coverage Q&A
* Damage assessment guidance
* Repair cost estimation
* Contractor lookup
* Claim filing guidance
* Claim status tracking
* Underinsurance alerts

---

# Key Features

## Persistent Memory

The application remembers:

* Property type
* Damage type
* Postcode
* Policy tier
* Claim ID

across multiple conversation turns without requiring users to repeat information.

---

## Agentic RAG

The system uses:

* Semantic retrieval over insurance policy documents
* Context-aware tool routing
* Citation-based responses

---

## Multi-Tool Architecture

### Policy RAG Retriever

Answers:

* Coverage questions
* Exclusions
* Add-ons
* Claims procedures

### Damage Cost Estimator

Provides:

* Indicative repair cost estimates
* Property-type-based filtering
* Damage-type-based lookup

### Contractor Network Lookup

Returns:

* Approved contractors
* Trade type
* Postcode-based filtering

### Claim Tracker

Tracks:

* Claim status
* Pending actions
* Claim workflow

---

# Tech Stack

| Layer         | Technology                |
| ------------- | ------------------------- |
| Backend       | FastAPI                   |
| Frontend      | Streamlit                 |
| LLM Framework | LangChain                 |
| Vector Store  | FAISS                     |
| Embeddings    | OpenAI Embeddings         |
| Memory        | Persistent Session Memory |
| Evaluation    | DeepEval + LangSmith      |
| Deployment    | Docker + AWS              |

---

# Project Structure

```bash
backend/
frontend/
datasets/
vector_store/
evaluation/
tests/
deployment/
docker/
```

---

# Setup Instructions

## 1. Clone Repository

```bash
git clone <repo-url>
cd property-insurance-ai-copilot
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

## 3. Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure Environment Variables

Create `.env`

```env
OPENAI_API_KEY=your_key
```

---

# Run Backend

```bash
uvicorn backend.api.main:app --reload
```

---

# Run Frontend

```bash
streamlit run frontend/app.py
```

---

# Docker Run

```bash
docker-compose up --build
```

---

# Evaluation

The system is evaluated using:

* DeepEval
* LangSmith
* Memory persistence tests
* Guardrail tests
* Faithfulness scoring
* Relevancy scoring

---

# Guardrails

The application blocks:

* Claim approval/rejection
* Binding repair quotes
* Fabricated contractor information
* Prompt injection attacks

---

# Future Enhancements

* Vision-based damage assessment
* Voice-enabled claims assistant
* Underinsurance calculator
* Multi-language support
* Real-time claims integration

---

# Authors

Capstone Project Team – Property Insurance AI Copilot

---

# Disclaimer

This project uses synthetic insurance data for educational and training purposes only.
