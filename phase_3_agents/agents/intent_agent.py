import os
import sys
import time
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import chromadb

load_dotenv()

def analyze_intent_batch(llm, batch_json_str):
    """Uses Groq to distinguish between bookmarking intent vs purchase delay intent for a batch."""
    prompt = PromptTemplate.from_template(
        """You are an expert user behavior analyst.
        Read the following JSON batch of user feedback about wishlisted fashion items.
        Determine each user's core intent. Respond with exactly ONE of the following options for each:
        
        - High Intent (Waiting for a specific trigger like a size restock or paycheck)
        - Medium Intent (Comparing across platforms, looking for reviews)
        - Low Intent (Purely bookmarking/window shopping, no plans to buy)
        - Unknown
        
        Input Format: A JSON array of objects with 'id' and 'text'.
        Output Format: You MUST return ONLY a valid JSON array of objects, where each object has the original 'id' and the assigned 'intent'. Do not include markdown blocks or any other text.
        
        Feedback Batch: {feedback}
        Output JSON:"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"feedback": batch_json_str})
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
    
    # Fetch a sample of up to 2000 documents
    try:
        results = collection.get(limit=2000) 
    except Exception as e:
        print(f"Error fetching from Chroma: {e}")
        return
    
    if not results['documents']:
        print("No documents found.")
        return
        
    # Prepare documents for batching (filtering out already analyzed ones)
    docs_to_process = []
    for idx, doc_text in enumerate(results['documents']):
        doc_id = results['ids'][idx]
        metadata = results['metadatas'][idx]
        if 'intent_level' not in metadata:
            docs_to_process.append({"id": doc_id, "text": doc_text, "metadata": metadata})
            
    if not docs_to_process:
        print("All fetched documents are already analyzed for intent.")
        return
        
    print(f"Found {len(docs_to_process)} unanalyzed documents. Analyzing intent with Groq in batches...")
    
    batch_size = 50
    updates_count = 0
    
    for i in range(0, len(docs_to_process), batch_size):
        batch = docs_to_process[i:i+batch_size]
        batch_input = [{"id": item["id"], "text": item["text"]} for item in batch]
        batch_json_str = json.dumps(batch_input)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response_text = analyze_intent_batch(llm, batch_json_str)
                # Clean up response (sometimes LLMs wrap json in markdown)
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3]
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3]
                
                output_json = json.loads(response_text.strip())
                
                # Map back to ChromaDB
                ids_to_update = []
                metadatas_to_update = []
                
                for out_item in output_json:
                    doc_id = out_item.get("id")
                    intent = out_item.get("intent")
                    
                    original_item = next((item for item in batch if item["id"] == doc_id), None)
                    if original_item:
                        meta = original_item["metadata"]
                        meta["intent_level"] = intent
                        ids_to_update.append(doc_id)
                        metadatas_to_update.append(meta)
                
                if ids_to_update:
                    collection.update(ids=ids_to_update, metadatas=metadatas_to_update)
                    updates_count += len(ids_to_update)
                    print(f"Successfully processed and updated batch of {len(ids_to_update)} documents.")
                
                time.sleep(5) # Rate limit protection between batches
                break
            except Exception as e:
                if '429' in str(e) or 'rate' in str(e).lower():
                    wait_time = 15 * (attempt + 1)
                    print(f"Rate limit hit. Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Error processing batch {i}: {e}")
                    print(f"Raw response was: {response_text if 'response_text' in locals() else 'None'}")
                    break
        
    print(f"Intent analysis complete! Updated {updates_count} documents.")

if __name__ == "__main__":
    run_intent_analyzer()
