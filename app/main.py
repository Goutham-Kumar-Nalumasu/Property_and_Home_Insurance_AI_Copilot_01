from fastapi import FastAPI
import sys
sys.path.append("/home/ubuntu/homeshield-insurance-copilot_02/app")
sys.path.append("/home/ubuntu/homeshield-insurance-copilot_02/app/tools")
from agent import run_agent
#from app.agent import run_agent
from document_loader import build_chunks
from memory import memory_manager
from rag import rag_retriever
from schemas import (
    ChatRequest,
    ChatResponse,
    DamageEstimateRequest,
    DamageEstimateResponse,
)
from damage_estimator import damage_estimator
from claim_status import get_claim_status
from faq_memory import faq_memory
from ingest_qdrant import ingest_chunks_to_qdrant




app = FastAPI(
    title="HomeShield Property Insurance Copilot API",
    version="1.0.0",
    description="Agentic RAG capstone API for HomeShield property insurance.",
)


@app.get("/")
async def root():
    return {
        "message": "HomeShield Property Insurance Copilot API is running.",
        "docs": "/docs",
    }


@app.post("/ingest")
async def ingest_documents():
    chunks = build_chunks()
    rag_retriever.reload()

    return {
        "message": "Documents ingested successfully.",
        "chunks_created": len(chunks),
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = run_agent(
            session_id=request.session_id,
            message=request.message,

        )

        return {
            "session_id": str(result.get("session_id", "")),

            "answer": str(result.get("answer", "")),

            "intent": str(result.get("intent", "")),

            "memory": result.get("memory", {}),

            "sources": [
                {
                    "document": str(source.get("document", "")),

                    "chunk_id": str(source.get("chunk_id", "")),

                    "score": float(source.get("score", 0)),

                    "text_preview": str(
                        source.get("text_preview", "")
                    ),
                }

                for source in result.get("sources", [])
            ]
        }

    except Exception as exc:
        import traceback

        error_trace = traceback.format_exc()

        print("========== CHAT ENDPOINT ERROR ==========")
        print(error_trace)
        print("=========================================")

        return {
            "answer": "Backend error occurred while processing your question.",
            "intent": "error",
            "memory": {},
            "sources": [],
            "error": str(exc),
            "traceback": error_trace,
        }


@app.get("/memory/{session_id}")
async def get_memory(session_id: str):
    return memory_manager.get(session_id)


@app.delete("/memory/{session_id}")
async def clear_memory(session_id: str):
    memory = memory_manager.clear(session_id)

    return {
        "message": "Memory cleared.",
        "memory": memory,
    }


@app.post("/estimate", response_model=DamageEstimateResponse)
async def estimate_damage(request: DamageEstimateRequest):
    result = damage_estimator.estimate(
        damage_type=request.damage_type,
        property_size_category=request.property_size_category,
        peril_category=request.peril_category,
        affected_component=request.affected_component,
    )

    return result


@app.get("/claim/{claim_id}")
async def claim_status(claim_id: str):
    return get_claim_status(claim_id)


@app.get("/faq/top")
async def top_faqs(limit: int = 10):
    return {
        "top_questions": faq_memory.get_top_questions(limit=limit)
    }

@app.post("/ingest/qdrant")
async def ingest_documents_to_qdrant():
    count = ingest_chunks_to_qdrant()

    return {
        "message": "Chunks ingested into Qdrant successfully.",
        "chunks_ingested": count,
        "vector_db": "Qdrant",
    }