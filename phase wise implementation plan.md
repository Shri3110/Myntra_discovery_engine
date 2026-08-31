# Phase-Wise Implementation Plan: AI-Powered Discovery Engine

This document outlines the step-by-step implementation strategy for the Myntra Wishlist Conversion Discovery Engine, based on the defined architecture.

## Phase 1: Foundation & Data Ingestion (Weeks 1-2)
**Goal:** Establish infrastructure and automate the collection of raw unstructured data.

*   **Task 1.1: Environment Setup**
    *   Set up cloud infrastructure (AWS S3 or GCS) for the Raw Data Lake.
    *   Deploy **n8n** (self-hosted) or configure a Zapier team account for orchestration.
*   **Task 1.2: API Integrations & Scrapers**
    *   Integrate Reddit API to pull daily posts/comments from `r/IndianFashionAddicts` and `r/IndiaMFA`.
    *   Integrate YouTube Data API to pull comments from top fashion haul videos.
    *   Set up app store review scrapers (Google Play & Apple App Store).
*   **Task 1.3: Data Pipeline Automation**
    *   Create n8n/Zapier workflows to trigger daily pulls and dump raw JSON payloads into the Data Lake.

## Phase 2: Processing & Vectorization (Weeks 3-4)
**Goal:** Clean, normalize, and vectorize the raw data to make it searchable and AI-ready.

*   **Task 2.1: Data Cleaning & Normalization**
    *   Write Python scripts to remove spam, bot comments, and redact PII.
    *   Implement basic translation/normalization for Hinglish and internet slang to standardize text.
*   **Task 2.2: Vector Database Setup**
    *   Provision a **Pinecone** or **Qdrant** database instance.
*   **Task 2.3: Embedding Pipeline**
    *   Integrate an embedding model (e.g., `text-embedding-3-small` or `voyage-large-2`).
    *   Automate the process of converting cleaned text into vector embeddings and storing them in the Vector DB with appropriate metadata (source, date, etc.).

## Phase 3: AI Agent Development (The Core) (Weeks 5-7)
**Goal:** Build and connect the LLM agents to extract meaningful qualitative insights from the data.

*   **Task 3.1: Classifier Agent**
    *   Prompt engineering with **Claude 3.5 Sonnet** to categorize incoming feedback into predefined themes (Sizing, Fit, Scarcity, Comparison, etc.).
    *   Set up nightly batch processing to categorize new incoming data.
*   **Task 3.2: Intent Analyzer Agent**
    *   Develop prompts to distinguish between "bookmarking intent" and "purchase delay intent" on wishlisted-style comments.
*   **Task 3.3: Synthesis & Q&A Agent (RAG)**
    *   Implement the RAG pipeline connecting the LLM to the Vector DB.
    *   Pre-program the agent to answer the specific discovery questions (e.g., "What role does social validation play?") based on retrieved context.

## Phase 4: Quantification & Dashboarding (Weeks 8-9)
**Goal:** Translate qualitative AI findings into a measurable format for Product Managers.

*   **Task 4.1: Aggregation Engine**
    *   Develop Pandas-based scripts to aggregate tagged data, calculating the volume/frequency of specific non-monetary barriers.
*   **Task 4.2: Opportunity Scoring Logic**
    *   Implement the scoring framework: `Opportunity Score = (Mention Volume) x (Sentiment Severity)`.
*   **Task 4.3: Interactive Dashboard**
    *   Build and deploy a **Streamlit** or **Gradio** application.
    *   Connect the dashboard to the Aggregation Engine to visualize top non-monetary opportunity areas, user segment trends, and verbatim examples.

## Phase 5: Testing, Refinement & Go-Live (Week 10)
**Goal:** Ensure the engine produces accurate, constraint-compliant, and actionable insights.

*   **Task 5.1: Constraint Validation**
    *   Rigorously test the RAG output to ensure it successfully filters out or deprioritizes monetary (discount/price drop) incentives as solutions.
*   **Task 5.2: End-to-End Testing**
    *   Run a simulated week of data through the entire pipeline (Ingestion -> Processing -> Agents -> Dashboard) to check for bottlenecks.
*   **Task 5.3: PM Handoff & Go-Live**
    *   Present the dashboard to the Growth Team, train them on querying the RAG Synthesis Agent, and deploy the system to production.
