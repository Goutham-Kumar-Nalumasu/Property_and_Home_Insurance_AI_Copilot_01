from fastapi import FastAPI

from app.agent import run_agent
from app.document_loader import build_chunks
from app.memory import memory_manager
from app.rag import rag_retriever
from app.schemas import ChatRequest, ChatResponse, DamageEstimateRequest, DamageEstimateResponse
from app.tools.damage_estimator import damage_estimator
from app.tools.claim_status import get_claim_status


app = FastAPI(
    title="HomeShield Property Insurance Copilot API",
    version="1.0.0",
    description="Agentic RAG capstone API for HomeShield property insurance.",
)


@app.get("/")
def root():
    return {
        "message": "HomeShield Property Insurance Copilot API is running.",
        "docs": "/docs",
    }


@app.post("/ingest")
def ingest_documents():
    chunks = build_chunks()
    rag_retriever.reload()
    return {
        "message": "Documents ingested successfully.",
        "chunks_created": len(chunks),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent(
        session_id=request.session_id,
        message=request.message,
    )
    return result


@app.get("/memory/{session_id}")
def get_memory(session_id: str):
    return memory_manager.get(session_id)


@app.delete("/memory/{session_id}")
def clear_memory(session_id: str):
    memory = memory_manager.clear(session_id)
    return {
        "message": "Memory cleared.",
        "memory": memory,
    }


@app.post("/estimate", response_model=DamageEstimateResponse)
def estimate_damage(request: DamageEstimateRequest):
    result = damage_estimator.estimate(
        damage_type=request.damage_type,
        property_size_category=request.property_size_category,
        peril_category=request.peril_category,
        affected_component=request.affected_component,
    )
    return result


@app.get("/claim/{claim_id}")
def claim_status(claim_id: str):
    return get_claim_status(claim_id)