"""
HomeShield Property Insurance Copilot package.
"""


from qdrant_client.http.exceptions import UnexpectedResponse

class LangChainQdrantRAG:

    def __init__(self):

        try:

            self.vector_store = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url
            )

            print("Existing Qdrant collection loaded.")

        except UnexpectedResponse:

            print("Collection not found. Creating new collection.")

            self.vector_store = QdrantVectorStore.from_documents(
                documents=[],
                embedding=self.embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url
            )