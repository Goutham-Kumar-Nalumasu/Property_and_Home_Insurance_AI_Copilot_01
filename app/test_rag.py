from langchain_qdrant_rag import rag_retriever

results = rag_retriever.search(
    query="What is home emergency cover?",
    top_k=5,
)

print("\nRESULT COUNT:", len(results))

for r in results:
    print("\n====================")
    print("DOCUMENT:", r["document"])
    print("SCORE:", r["score"])
    print("TEXT:", r["text"][:300])
