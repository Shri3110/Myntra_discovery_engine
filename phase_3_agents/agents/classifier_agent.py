import os
import sys
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import chromadb

load_dotenv()

def get_unclassified_documents(collection):
    """Fetch documents from ChromaDB that haven't been classified yet."""
    results = collection.get(
        where={"category": {"$exists": False}}
    )
    return results

def classify_feedback(llm, text):
    """Uses Groq to classify the feedback into predefined non-monetary categories."""
    prompt = PromptTemplate.from_template(
        """You are an expert AI product manager for a fashion e-commerce app.
        Analyze the following user feedback regarding items they have wishlisted but not purchased.
        Categorize the feedback into exactly ONE of the following categories that best represents the primary barrier:
        
        - Sizing/Fit Uncertainty
        - Comparison Paralysis (too many options)
        - Waiting for Validation (social proof, reviews, styling ideas)
        - High Friction (returns policy, bad UI)
        - Pure Bookmarking (no immediate purchase intent)
        - Unknown (if none apply)
        
        Do not include any other text, just the category name.
        
        Feedback: {feedback}
        Category:"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"feedback": text})
    return response.content.strip()

def run_classifier():
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY is not set in .env")
        return

    # Initialize Groq LLM (Using Mixtral)
    llm = ChatGroq(temperature=0, model_name="qwen/qwen3.8-27b")
    
    # Connect to local ChromaDB from Phase 2
    chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'phase_2_processing', 'chroma_db'))
    if not os.path.exists(chroma_db_dir):
        print(f"ChromaDB not found at {chroma_db_dir}. Please run Phase 2 first.")
        return
        
    client = chromadb.PersistentClient(path=chroma_db_dir)
    collection = client.get_collection(name="myntra_feedback")
    
    # We will just fetch a small batch to classify for this script
    results = collection.get(limit=100) # In production we would filter by missing category metadata
    
    if not results['documents']:
        print("No documents found to classify.")
        return
        
    print(f"Found {len(results['documents'])} documents. Classifying with Groq...")
    
    updates_count = 0
    for idx, doc_text in enumerate(results['documents']):
        doc_id = results['ids'][idx]
        metadata = results['metadatas'][idx]
        
        # Skip if already classified
        if 'category' in metadata:
            continue
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                category = classify_feedback(llm, doc_text)
                print(f"ID {doc_id} -> {category.encode('ascii', 'ignore').decode('ascii')}")
                
                # Update metadata in ChromaDB
                metadata['category'] = category
                collection.update(
                    ids=[doc_id],
                    metadatas=[metadata]
                )
                time.sleep(5) # Prevent Groq rate limits when processing 250 reviews
                updates_count += 1
                break
            except Exception as e:
                if '429' in str(e) or 'rate' in str(e).lower():
                    wait_time = 15 * (attempt + 1)
                    print(f"Rate limit hit. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Error processing {doc_id}: {e}")
                    break
        
    print(f"Classification complete! Updated {updates_count} documents.")

if __name__ == "__main__":
    run_classifier()
