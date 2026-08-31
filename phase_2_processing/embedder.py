import os
import json
import chromadb
from chromadb.config import Settings
import uuid

def initialize_chromadb(db_path):
    """Initializes the local ChromaDB client."""
    os.makedirs(db_path, exist_ok=True)
    # Using PersistentClient so the database saves to disk
    client = chromadb.PersistentClient(path=db_path)
    
    # Create or get the collection
    collection = client.get_or_create_collection(
        name="myntra_feedback",
        metadata={"description": "User feedback from various sources regarding Myntra wishlists"}
    )
    return collection

def embed_data(input_dir, collection):
    """Reads cleaned JSON files and adds them to ChromaDB."""
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' not found. Please run cleaner.py first.")
        return

    documents = []
    metadatas = []
    ids = []
    
    # Iterate through all cleaned files
    for filename in os.listdir(input_dir):
        if filename.startswith("cleaned_") and filename.endswith(".json"):
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in data:
                # We embed the cleaned text
                text = item.get('cleaned_text')
                if not text:
                    continue
                    
                documents.append(text)
                
                # Metadata to filter later (e.g. source, rating, user)
                metadata = {
                    "source": item.get('source', 'Unknown'),
                    "original_id": str(item.get('id', '')),
                }
                # Add optional metadata safely
                if 'rating' in item and item['rating'] is not None:
                    metadata['rating'] = int(item['rating'])
                    
                metadatas.append(metadata)
                
                # Generate a unique ID for Chroma
                ids.append(str(uuid.uuid4()))

    if documents:
        print(f"Embedding {len(documents)} documents into Chroma DB... This may take a moment to download the model the first time.")
        
        # Batch inserting into ChromaDB (it automatically handles generating embeddings)
        batch_size = 500
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                ids=ids[i:i+batch_size]
            )
            print(f"Inserted batch {i//batch_size + 1}")
            
        print("Vectorization complete!")
    else:
        print("No documents found to embed.")

if __name__ == "__main__":
    cleaned_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data_cleaned'))
    chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'chroma_db'))
    
    print("Initializing Vector Database...")
    collection = initialize_chromadb(chroma_db_dir)
    
    print("Starting Embedding Pipeline...")
    embed_data(cleaned_data_dir, collection)
