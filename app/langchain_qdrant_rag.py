import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.exceptions import UnexpectedResponse

load_dotenv()


class LangChainQdrantRAG:

    def __init__(self):

        self.collection_name = os.getenv(
            "QDRANT_COLLECTION",
            "homeshield_policy_docs",
        )

        self.qdrant_url = os.getenv(
            "QDRANT_URL",
            "http://localhost:6333",
        )

        self.qdrant_api_key = os.getenv(
            "QDRANT_API_KEY"
        ) or None

        self.embeddings = OpenAIEmbeddings(
            model=os.getenv(
                "OPENAI_EMBEDDING_MODEL",
                "text-embedding-3-small",
            ),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        try:

            # Load existing collection
            self.vector_store = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
            )

            print(
                f"Loaded existing collection: "
                f"{self.collection_name}"
            )

        except UnexpectedResponse:

            print(
                f"Collection '{self.collection_name}' "
                f"not found."
            )

            print(
                "Please run ingestion first."
            )

            self.vector_store = None

    def search(
        self,
        query: str,
        top_k: int = 10,
        policy_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:

        if not self.vector_store:
            return []

        docs_with_scores = (
            self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k,
                
            )
        )

        results = []

        for doc, score in docs_with_scores:

            metadata = doc.metadata or {}

            if policy_type:

                doc_policy_type = metadata.get(
                    "policy_type"
                )

                if (
                    doc_policy_type
                    and doc_policy_type != policy_type
                ):
                    continue

            results.append(
                {
                    "text": doc.page_content,
                    "score": float(score),
                    "document": metadata.get(
                        "document",
                        "unknown"
                    ),
                    "chunk_id": metadata.get(
                        "chunk_id",
                        -1
                    ),
                    "policy_type": metadata.get(
                        "policy_type",
                        "unknown"
                    ),
                }
            )

        return results


rag_retriever = LangChainQdrantRAG()