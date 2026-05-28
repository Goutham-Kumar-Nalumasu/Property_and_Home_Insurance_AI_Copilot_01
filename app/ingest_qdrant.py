import json
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

from config import settings

import os

load_dotenv()


def load_chunks() -> List[Document]:
    if not settings.CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {settings.CHUNKS_FILE}. "
            "Run python -m app.document_loader first."
        )

    with open(settings.CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "document": chunk.get("document"),
                    "chunk_id": chunk.get("chunk_id"),
                    "policy_type": chunk.get("policy_type"),
                },
            )
        )

    return documents


def ingest_chunks_to_qdrant() -> int:
    docs = load_chunks()

    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    QdrantVectorStore.from_documents(
        documents=docs,
        embedding=embeddings,
        url=os.getenv("QDRANT_URL", "http://localhost:6333"),
        api_key=os.getenv("QDRANT_API_KEY") or None,
        collection_name=os.getenv(
            "QDRANT_COLLECTION",
            "homeshield_policy_docs",
        ),
    )

    return len(docs)


if __name__ == "__main__":
    count = ingest_chunks_to_qdrant()
    print(f"Ingested {count} chunks into Qdrant.")