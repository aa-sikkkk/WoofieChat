from sentence_transformers import SentenceTransformer
import chromadb 
from chromadb.config import Settings
import os
import re


# loading the Dataset but for this Project I'll use MarkDown file for easy access.

def loadsinglefile(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

        pattern = r"### (.*?)\n(.*?)(?=\n### |\Z)" # For finding the data
        matches = re.findall(pattern, text, re.DOTALL)
        faq_pairs = [{"question": q.strip(), "answer": a.strip()} for q,a in matches]

    return faq_pairs

def LoadData(folder_path="data"):
    all_faqs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)
            faq_pairs = loadsinglefile(file_path)
            for pair in faq_pairs:
                pair["source"] = filename # This is for tracking the source file
            all_faqs.extend(faq_pairs)
    return all_faqs

def embeddata(data_folder = "data"):
    print("Loading Data...")
    faq_data = LoadData(data_folder)
    print("Data Loaded.")

    print("Embedding Data...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("Loading chromaDB...")
    chroma_client = chromadb.PersistentClient(path="db")
    collection = chroma_client.get_or_create_collection(name="woofieData")

    print("Embedding and Adding Data to chromaDB...")
    for i, item in enumerate(faq_data):
        text = f"{item['question']} {item['answer']}"
        embedding = model.encode(text).tolist()
       
        collection.add(
            ids=[f"faq_{i}"],
            documents=[text],
            embeddings=[embedding],
            metadatas = [{
                "question": item["question"],
                "answer": item["answer"],
                "source": item.get("source", "unknown")
            }]
        )
        
    print("Done! Stored",len(faq_data),"Individuals data embeddings")

if __name__ == "__main__":
    embeddata()
   

