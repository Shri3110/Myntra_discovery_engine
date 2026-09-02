import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def run_synthesis_query(question):
    """
    Runs a RAG pipeline to answer product/growth questions based on the feedback database,
    strictly ignoring monetary incentives as a solution.
    """
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY is not set in .env")
        return

    # Initialize Groq LLM (Mixtral)
    llm = ChatGroq(temperature=0.2, model_name="qwen/qwen3.8-27b")
    
    # Initialize the same embedding model used in Phase 2
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Connect to local ChromaDB
    chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'phase_2_processing', 'chroma_db'))
    if not os.path.exists(chroma_db_dir):
        print("ChromaDB not found. Please run Phase 2 first.")
        return
        
    vectorstore = Chroma(
        collection_name="myntra_feedback", 
        embedding_function=embeddings,
        persist_directory=chroma_db_dir
    )
    
    # Setup custom prompt enforcing the NON-MONETARY constraint
    template = """You are a senior Product Manager for Myntra's Growth Team.
    Your goal is to answer questions about user behavior based on the provided user feedback.
    
    CRITICAL CONSTRAINT: You CANNOT propose or highlight monetary incentives (discounts, price drops, coupons, sales) as a solution or a primary reason for behavior, even if users mention them. You must focus on UX, psychology, styling, fit, social validation, and comparison friction.
    
    Context (Raw User Feedback):
    {context}
    
    Question: {question}
    
    Detailed Analysis:"""
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    
    # Create the RAG Chain
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 10}), # Retrieve top 10 relevant feedback items
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    print(f"\nAnalyzing: '{question}'...")
    response = qa_chain.invoke({"query": question})
    print("\n" + "="*50)
    print("INSIGHT REPORT:")
    print("="*50)
    print(response['result'])
    print("="*50 + "\n")

if __name__ == "__main__":
    # Example questions provided in the original problem statement
    sample_questions = [
        "What uncertainties remain after users have identified a product they like?",
        "What role do fit, size, styling, price, reviews, occasion and social validation play?",
        "Why do users add fashion products to their wishlist but stop short of purchasing?"
    ]
    
    print("Starting RAG Synthesis Agent...")
    # Run the first question as a test
    run_synthesis_query(sample_questions[0])
