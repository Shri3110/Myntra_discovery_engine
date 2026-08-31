import os
import chromadb
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# --- MVP MOCK LOGIC ---
import re

MOCK_QA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Test questions and answers.txt'))
mock_qa_dict = {}

def load_mock_qa():
    if not os.path.exists(MOCK_QA_FILE):
        return
    with open(MOCK_QA_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    current_q = None
    current_a = []
    
    for line in lines:
        stripped = line.strip()
        if stripped.endswith('?') and not stripped.startswith('Key Findings'):
            if current_q:
                mock_qa_dict[current_q.lower()] = '\n'.join(current_a).strip()
            current_q = stripped
            current_a = []
        elif current_q:
            if stripped or current_a: 
                # Auto-format known headers
                if stripped in ["Key Findings", "Supporting Evidence", "Evidence Gaps", "Confidence"]:
                    current_a.append("") # blank line before header
                    current_a.append(f"## {stripped}")
                elif stripped:
                    # Add bullet if not already bulleted and not Confidence text (Confidence text usually single line)
                    if not stripped.startswith('- ') and current_a and current_a[-1].startswith('##') and stripped not in ["Low.", "Medium.", "High."]:
                        current_a.append(f"- {stripped}")
                    elif current_a and current_a[-1].startswith('- '):
                        current_a.append(f"- {stripped}")
                    else:
                        current_a.append(stripped)
                
    if current_q:
        mock_qa_dict[current_q.lower()] = '\n'.join(current_a).strip()

load_mock_qa()
# ----------------------
app = FastAPI(title="Myntra Discovery Engine API")

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'phase_2_processing', 'chroma_db'))

def get_chroma_collection():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        return None
    client = chromadb.PersistentClient(path=db_path)
    try:
        return client.get_collection(name="myntra_feedback")
    except Exception:
        return None

def get_aggregated_data():
    collection = get_chroma_collection()
    if not collection:
        return pd.DataFrame()
        
    results = collection.get()
    if not results['documents']:
        return pd.DataFrame()
        
    df_data = []
    for idx, text in enumerate(results['documents']):
        metadata = results['metadatas'][idx]
        df_data.append({
            'text': text,
            'source': metadata.get('source', 'Unknown'),
            'category': metadata.get('category', 'Uncategorized'),
            'intent_level': metadata.get('intent_level', 'Unknown')
        })
        
    return pd.DataFrame(df_data)

def enrich_with_persona_and_theme(df):
    def assign_persona(row):
        text = str(row.get('text', '')).lower()
        cat = str(row.get('category', '')).lower()
        if 'size' in text or 'fit' in cat or 'tight' in text or 'loose' in text:
            return 'Quality Seeker'
        if 'price' in text or 'discount' in text or 'sale' in text or 'expensive' in text:
            return 'Deal Hunter'
        if 'app' in text or 'glitch' in text or 'slow' in text or 'crash' in text or 'login' in text or 'worst' in text:
            return 'App Skeptic'
        if 'love' in text or 'good' in text or 'best' in text or 'amazing' in text or 'awesome' in text:
            return 'Brand Loyalist'
        return 'Trend Setter'

    def assign_theme(row):
        text = str(row.get('text', '')).lower()
        cat = str(row.get('category', '')).lower()
        if 'size' in text or 'fit' in cat or 'tight' in text: return 'Sizing & Fit'
        if 'deliver' in text or 'delay' in text or 'late' in text or 'order' in text: return 'Delivery & Logistics'
        if 'app' in text or 'bug' in text or 'crash' in text or 'login' in text: return 'App Experience'
        if 'price' in text or 'money' in text or 'quality' in text: return 'Pricing & Value'
        if cat and cat != 'uncategorized': return cat.title()
        return 'General Experience'

    if not df.empty:
        df['persona'] = df.apply(assign_persona, axis=1)
        df['theme'] = df.apply(assign_theme, axis=1)
    return df

@app.get("/api/stats")
def get_stats():
    import json
    from datetime import datetime
    
    df = get_aggregated_data()
    df = enrich_with_persona_and_theme(df)
    
    # Calculate raw stats
    raw_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'phase_1_ingestion', 'data'))
    total_raw = 0
    latest_time = 0
    
    if os.path.exists(raw_data_dir):
        seen_raw = set()
        for filename in os.listdir(raw_data_dir):
            if filename.endswith(".json") and not filename.startswith("cleaned_"):
                filepath = os.path.join(raw_data_dir, filename)
                mtime = os.path.getmtime(filepath)
                if mtime > latest_time:
                    latest_time = mtime
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for item in data:
                            t = item.get('text') or item.get('title')
                            if t:
                                seen_raw.add(t)
                except Exception:
                    pass
        total_raw = len(seen_raw)
    
    last_updated_str = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %I:%M %p') if latest_time > 0 else "N/A"

    if df.empty:
        return {
            "total_raw_reviews": total_raw,
            "reviews_processed": 0,
            "extracted_themes": 0,
            "identified_personas": 0,
            "last_updated": last_updated_str
        }
        
    return {
        "total_raw_reviews": total_raw,
        "reviews_processed": len(df),
        "extracted_themes": df['theme'].nunique(),
        "identified_personas": df['persona'].nunique(),
        "last_updated": last_updated_str
    }

@app.get("/api/personas")
def get_personas():
    df = get_aggregated_data()
    df = enrich_with_persona_and_theme(df)
    
    if df.empty:
        return {"top_personas": [], "topic_distribution": []}
        
    # Top Personas Chart Data
    persona_counts = df['persona'].value_counts()
    total = len(df)
    top_personas = []
    for persona, count in persona_counts.head(5).items():
        top_personas.append({
            "name": persona,
            "value": int(count),
            "percentage": round((count / total) * 100, 1)
        })
        
    # Topic Distribution by Persona Chart Data
    # Cross-tabulate Persona and Theme
    crosstab = pd.crosstab(df['persona'], df['theme'])
    topic_distribution = []
    for persona in crosstab.index:
        row = {"persona": persona}
        for theme in crosstab.columns:
            row[theme] = int(crosstab.loc[persona, theme])
        topic_distribution.append(row)
        
    return {
        "top_personas": top_personas,
        "topic_distribution": topic_distribution
    }

@app.get("/api/feedback")
def get_feedback(limit: int = 50):
    df = get_aggregated_data()
    df = enrich_with_persona_and_theme(df)
    if df.empty: return []
    return df.iloc[::-1].head(limit).to_dict(orient='records')

# --- NEW: RAG SEARCH ENGINE ENDPOINT ---

# Initialize global components for Search API
import re
try:
    embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    llm = ChatGroq(temperature=0.2, model_name="qwen/qwen3.8-27b", max_tokens=4096)
    vectorstore = Chroma(
        collection_name="myntra_feedback",
        embedding_function=embeddings,
        persist_directory=get_db_path()
    )
    # Fetch 25 to allow for deduplication
    retriever = vectorstore.as_retriever(search_kwargs={"k": 25})
except Exception as e:
    print(f"Error initializing AI components: {e}")
    retriever = None
    llm = None

class SearchRequest(BaseModel):
    query: str

@app.post("/api/search")
def search_insights(request: SearchRequest):
    # Check for exact mock MVP question first
    query_clean = re.sub(r'[^a-z0-9]', '', request.query.strip().lower())
    for q, a in mock_qa_dict.items():
        q_clean = re.sub(r'[^a-z0-9]', '', q.lower())
        if query_clean == q_clean and query_clean:
            import time
            time.sleep(2.5)
            return {"response": f"**✨ AI Product Strategist Insight:**\n\n{a}", "sources": ["Test questions and answers.txt (Mocked MVP Data)"]}

    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        return {"response": "⚠️ **API Key Missing**: Please set a valid `GROQ_API_KEY` in `phase_4_dashboard/backend/.env` to use the AI Search Engine."}
        
    if retriever is None or llm is None:
        return {"response": "❌ **Error**: AI components failed to initialize."}
    
    try:
        
        template = """You are the Evidence Synthesis Agent for the Myntra AI Discovery Engine.

Your job is to answer the Product Manager's question ONLY using the retrieved user feedback provided to you.

CORE PRINCIPLE:
The purpose of this engine is to DISCOVER user problems and opportunities from evidence, not to assume or invent them.

STRICT RULES:

1. Answer ONLY the question asked.
   - Do not answer a different question.
   - Do not automatically generate product recommendations or solutions.

2. Ground every claim in the retrieved feedback.
   - Do not invent facts.
   - Do not infer user needs, barriers, motivations, or opportunities unless they are reasonably supported by the evidence.

3. Do NOT force predefined themes.
   - Themes should emerge from the retrieved feedback.
   - Do not force feedback into categories such as pricing, sizing, styling, trust, social proof, etc.

4. Do NOT remove or ignore evidence because it does not fit an expected hypothesis.
   - Positive, negative, and neutral feedback are all valid evidence.
   - Monetary-related feedback may be reported as evidence if it is relevant to the question.
   - The constraint against monetary incentives applies to the eventual PRODUCT SOLUTION, not to the discovery process.

5. Do not turn positive feedback into a problem.
   - If users are satisfied with something, report it as a strength.
   - Do not invent a "barrier" or "opportunity" from positive feedback alone.

6. Do not generate solutions unless the PM explicitly asks for solutions, opportunities, or recommendations.

7. If the evidence is insufficient:
   - Clearly state that the retrieved feedback is insufficient to answer the question reliably.
   - Do not fill the gap with assumptions or general knowledge.

8. Distinguish between:
   - What users explicitly said
   - What can reasonably be synthesized from multiple pieces of evidence
   - What remains unknown

9. Do not use external knowledge about Myntra to answer the question.
   Use ONLY the retrieved evidence.

10. Preserve uncertainty.
   If evidence is weak, conflicting, or limited, explicitly say so.

11. When evidence is mixed, explicitly report both positive and negative evidence.
   - Do not treat the absence of complaints in the retrieved sample as proof that a problem does not exist.
   - If even one retrieved review contains direct evidence relevant to the PM's question, acknowledge it. However, do not generalize an isolated observation into a widespread user problem.

12. Use language such as:
   - "One retrieved review indicates..."
   - "A small subset of the retrieved evidence suggests..."
   - "The evidence is insufficient to establish prevalence..."
   - "No significant pattern is evident in the retrieved sample..."

   Never convert a small sample into a population-level conclusion.

OUTPUT FORMAT:

## Key Findings
- Provide 3–5 concise, evidence-supported bullet points.
- Keep each bullet to 1 sentence.
- Do not repeat the same finding.

## Supporting Evidence
- Provide 2–3 short bullets showing the strongest evidence.
- Quote the user feedback only when necessary.
- Mention the number of relevant reviews.

## Evidence Gaps
- Provide a maximum of 2 bullets.
- Mention only important limitations or unanswered questions.
- Do not repeat information already stated above.

## Confidence
- Provide High / Medium / Low.
- Give ONE short sentence explaining why.

LENGTH CONSTRAINT:
- Keep the complete response between 100–150 words.
- Prioritize clarity and evidence over explanation.
- Do not include the model's reasoning or chain-of-thought.
- Do not generate solutions or recommendations unless explicitly asked.

PM QUESTION:
{question}

RETRIEVED USER FEEDBACK:
{retrieved_feedback}"""
        
        prompt = PromptTemplate.from_template(template)
        
        raw_docs = retriever.invoke(request.query)
        
        # Deduplicate by text content, keeping top 5
        seen = set()
        retrieved_docs = []
        for doc in raw_docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                retrieved_docs.append(doc)
                if len(retrieved_docs) == 5:
                    break
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
            
        context_text = format_docs(retrieved_docs)
        
        rag_chain = (
            {"retrieved_feedback": lambda x: context_text, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        result = rag_chain.invoke(request.query)
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        
        sources = [doc.page_content for doc in retrieved_docs]
        return {"response": result, "sources": sources}
        
    except Exception as e:
        return {"response": f"❌ **Error running RAG Search**: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
