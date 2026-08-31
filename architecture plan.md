# Architecture Plan: AI-Powered Discovery Engine (Myntra Wishlist Conversion)

## 1. System Overview
The Discovery Engine is designed to ingest multi-channel user feedback at scale, process it using AI agents, and synthesize qualitative insights into quantifiable opportunity areas. The goal is to uncover non-monetary barriers preventing users from purchasing wishlisted items within 30 days.

## 2. Architecture Components

### 2.1 Data Ingestion Layer
Responsible for gathering structured and unstructured data from various platforms.
*   **Sources:**
    *   **App Stores:** Google Play Store & Apple App Store reviews (via AppTweak or scraper APIs).
    *   **Communities:** Reddit (e.g., `r/IndianFashionAddicts`, `r/IndiaMFA`) via Reddit API.
    *   **Social & Video:** YouTube comments (via YouTube Data API) on fashion haul videos, Twitter/X mentions.
    *   **Internal Data (Simulated):** Public product reviews and Q&A sections from fashion e-commerce platforms.
*   **Orchestration:** **n8n** (self-hosted) or **Zapier** to schedule daily/weekly data pulls.
*   **Storage:** 
    *   **Raw Data Lake:** Amazon S3 or Google Cloud Storage for immutable raw data storage.
    *   **Vector Database:** **Pinecone** or **Qdrant** to store embeddings for semantic search and RAG (Retrieval-Augmented Generation).

### 2.2 Data Processing & Enrichment Layer
Cleans and prepares data for AI consumption.
*   **Cleaning:** Removal of spam, bot comments, and PII (Personally Identifiable Information) redaction.
*   **Translation & Normalization:** Handling Hinglish (Hindi + English) and internet slang using a lightweight local LLM or API.
*   **Embedding Generation:** Using models like `text-embedding-3-small` (OpenAI) or `voyage-large-2` to vectorize the cleaned text for semantic search.

### 2.3 AI Analysis & Discovery Engine (The Core)
This layer utilizes specialized AI agents working in a pipeline to analyze the context and intent behind the data.
*   **LLM Choice:** **Claude 3.5 Sonnet** (excellent at nuanced reasoning and structured data extraction) and **GPT-4o**.
*   **Agentic Workflow (Multi-Agent Setup):**
    1.  **Classifier Agent:** Scans incoming feedback and tags it with predefined and dynamically generated categories (e.g., *Fit Uncertainty*, *Comparison Paralysis*, *Bookmarking Behavior*, *Out of Stock/Size*).
    2.  **Intent Analyzer Agent:** Determines the underlying intent. Distinguishes if a user wishlisted an item as a "maybe later" (low intent) vs. "waiting for a specific trigger" (high intent, e.g., waiting for restock or size confirmation).
    3.  **Synthesis & Q&A Agent (RAG):** Uses RAG to query the vector database and answer the specific discovery questions (e.g., "What information do users seek outside Myntra before purchasing?").

### 2.4 Quantification & Analytics Layer
Bridges the gap between qualitative text and quantitative metrics to influence business decisions.
*   **Aggregation Engine:** Python-based scripts (Pandas) to group categorized insights and calculate frequencies (e.g., "34% of Reddit discussions about wishlists mention sizing inconsistencies").
*   **Opportunity Scoring:** An algorithm that scores identified problems based on:
    *   **Volume:** How often the issue is mentioned.
    *   **Sentiment Severity:** How strongly negative the sentiment is around the barrier.
*   **Visualization:** A **Streamlit** or **Gradio** web app to serve as an interactive dashboard for Product Managers to explore the data, filter by user segments, and view the top quantified opportunity areas.

## 3. Workflow Diagram (Logical Flow)

1. **Trigger:** n8n cron job runs every 24 hours.
2. **Fetch:** n8n calls APIs (Reddit, Play Store, YouTube) -> JSON payloads.
3. **Process:** Python script cleans text and generates embeddings.
4. **Store:** Embeddings saved to Pinecone; Raw JSON saved to S3.
5. **Analyze:** 
   - Nightly batch job runs Classifier Agent over new data.
   - Synthesis Agent aggregates weekly trends.
6. **Output:** Dashboard updates with new quantitative metrics and qualitative summaries highlighting why users are postponing purchases.

## 4. Key Considerations for the Constraint
Since **monetary incentives (discounts) are prohibited**, the engine is explicitly prompted to filter out or deprioritize "price drop" as a solution. Instead, the AI agents are directed to extract insights related to:
*   Social proof and styling validation.
*   Size/Fit confidence (e.g., virtual try-on needs, user-generated photos).
*   Scarcity or FOMO (without price manipulation).
*   Cognitive load during comparison of similar wishlisted items.
