from langchain.tools import tool
import chromadb
#import uuid 

# Persistent client
chroma_client = chromadb.PersistentClient(path="./chroma_data")

collection = chroma_client.get_or_create_collection(
    name="hiking_spots"
)

@tool
def search_hiking_spots(query: str) -> str:
    """
    Searches the hiking and nature knowledge base for relevant information.
    """

    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    documents = results.get("documents", [])

    if not documents or not documents[0]:
        return "No relevant hiking or nature information found."

    retrieved_text = "\n\n".join(documents[0])

    return f"Relevant Hiking & Nature Information:\n\n{retrieved_text}"
