import os
import sys
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import chromadb

load_dotenv()

def analyze_intent(llm, text):
    """Uses Groq to distinguish between bookmarking intent vs purchase delay intent."""
    prompt = PromptTemplate.from_template(
        """You are an expert user behavior analyst.
        Read the following user feedback about wishlisted fashion items.
        Determine the user's core intent. Respond with exactly ONE of the following options:
        
        - High Intent (Waiting for a specific trigger like a size restock or paycheck)
        - Medium Intent (Comparing across platforms, looking for reviews)
        - Low Intent (Purely bookmarking/window shopping, no plans to buy)
        - Unknown
        
        Feedback: {feedback}
        Intent:"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"feedback": text})
    return response.content.strip()

def run_intent_analyzer():
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY is not set in .env")
        return

    # Initialize Groq LLM
    llm = ChatGroq(temperature=0, model_name="qwen/qwen3.8-27b")
    
    chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'phase_2_processing', 'chroma_db'))
    if not os.path.exists(chroma_db_dir):
        print("ChromaDB not found. Please run Phase 2 first.")
        return
        
    client = chromadb.PersistentClient(path=chroma_db_dir)
    collection = client.get_collection(name="myntra_feedback")
    
    # We will fetch a small batch to analyze
    results = collection.get(limit=100) 
    
    if not results['documents']:
        print("No documents found.")
        return
        
    print(f"Found {len(results['documents'])} documents. Analyzing intent with Groq...")
    
    updates_count = 0
    for idx, doc_text in enumerate(results['documents']):
        doc_id = results['ids'][idx]
        metadata = results['metadatas'][idx]
        
        # Skip if already analyzed
        if 'intent_level' in metadata:
            continue
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                intent = analyze_intent(llm, doc_text)
                print(f"ID {doc_id} -> {intent.encode('ascii', 'ignore').decode('ascii')}")
                
                # Update metadata in ChromaDB
                metadata['intent_level'] = intent
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
        
    print(f"Intent analysis complete! Updated {updates_count} documents.")

if __name__ == "__main__":
    run_intent_analyzer()
