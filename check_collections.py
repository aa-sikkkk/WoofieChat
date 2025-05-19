import chromadb

def list_collections():
    """List all available collections in the ChromaDB"""
    chroma_client = chromadb.PersistentClient(path="db")
    collections = chroma_client.list_collections()
    print("Available collections:")
    for collection in collections:
        print(f"- {collection.name}")

if __name__ == "__main__":
    list_collections()
