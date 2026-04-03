# AI-Powered Government Scheme Recommendation System (Winner-Level AI)

A robust, production-ready FastAPI backend designed to instantly recommend highly relevant government schemes to citizens using a hybrid approach of **Retrieval Augmented Generation (RAG)** and **Probabilistic Confidence Scoring (Fuzzy Logic)**. 

Additionally, this repository includes a **LangGraph-based Multi-Agent Prototype**, capable of executing multi-step conversational and analytical workflows.

## 🚀 Key Innovations & Architecture

This system has evolved from a strict rule-based filter into an intelligent, scalable AI engine.

### 1. 🧠 High-Density RAG Pipeline (FastAPI)
We use `sentence-transformers/all-MiniLM-L6-v2` securely stored in a local FAISS index. Instead of merely mapping a single field, the engine constructs a dense semantic foundation by fusing:
`combined_text = search_text + summary + keywords`
This ensures unparalleled semantic retrieval accuracy without calling external paid APIs.

### 2. 📊 Probabilistic Eligibility (Fuzzy Logic)
Real-world users rarely match 100% of stringent government logic perfectly. We abolished strict boolean filtering and replaced it with an intelligent **Confidence Engine**:
`confidence = matched_conditions / total_conditions`
- **1.0**: Full Match (Eligible)
- **0.6 – 0.9**: Partial Match (Likely Eligible)
- **< 0.5**: Not Eligible (Discarded)

### 3. 🏆 Multi-Factor Intelligence Ranking
We do not sort simply by priority score. Outcomes are algorithmically ranked using a blended formula:
`final_score = (0.5 * Confidence) + (0.3 * Priority Score) + (0.2 * FAISS Semantic Similarity)`
This guarantees the absolute best, most personalized recommendations surface first.

### 4. 🤖 LangGraph Multi-Agent Orchestration
Beyond the core recommendation API, we have developed a powerful modular multi-agent workflow using **LangGraph**. The workflow cascades through continuous stages:
- **Retrieval Agent**: Semantically searches the dataset based on inputs.
- **Eligibility Agent**: Filters retrieved results mapped against the user's explicit profile limits.
- **Policy Interpretation Agent**: (LLM Simulated) Analyzes eligible schemes logically to glean final deep insights for the user.
- **Recommendation Agent**: Formats and synthesizes the final output dynamically.

### 5. 🛡️ Absolute System Robustness & Safety
- **Data Guard Layer (Pre-load Validation)**: Malformed JSON arrays missing critical keys are forcefully rejected during startup, guaranteeing zero runtime crashes.
- **State Normalization**: All incoming string evaluations invoke our `_normalize()` pipeline (strip + lowercase) rendering bugs between `"Uttar Pradesh"` and `"up"` obsolete.
- **No-Match Fallbacks**: In the rare event a user profile generates 0 matches, the API catches the boundaries and legally returns a structured `"No Match Found"` dummy profile, keeping UI rendering flawless.

### 6. 💎 Premium Rich Responses
API returns are completely augmented for UI richness. Beyond basic titles and links, the backend explicitly renders:
- `match_type` (Full / Partial)
- `category`
- `documents_required`
- `priority_tag` (High Benefit / Standard)

---

## 🏗️ Folder Structure

```text
backend/
├── app/                            # Core FastAPI Backend
│   ├── main.py                     # App entrypoint (Triggers Caching)
│   ├── routes.py                   # API Endpoint controllers
│   ├── models.py                   # Premium Validation schemas
│   ├── services/
│   │   ├── rag.py                  # Dense FAISS semantic engine
│   │   ├── eligibility.py          # Fuzzy matching & normalizer
│   │   └── recommendation.py       # Multi-factor ranking orchestration
│   └── utils/
│       ├── embeddings.py           # Model singleton
│       └── loader.py               # Pre-validation memory wrapper
│
├── project/                        # LangGraph Multi-Agent Prototype
│   ├── main.py                     # CLI Entry point for running the graph
│   ├── graph.py                    # Node and Edge definitions
│   ├── state.py                    # Multi-agent typed dict schemas
│   ├── dataset.py                  # Dynamic offline data loader 
│   └── agents/                     # Modular Agents code
│       ├── retrieval_agent.py
│       ├── eligibility_agent.py
│       ├── policy_agent.py
│       └── recommendation_agent.py
│
├── schemes_master.json             # Root Scheme Dataset utilized by both engines
└── requirements.txt                # Root Dependencies
```

---

## 💻 Installation & Setup

1. **Navigate to the terminal** in this directory:
   ```bash
   cd path/to/backend
   ```
2. **Install Lightweight Dependencies**:
   ```bash
   pip install -r requirements.txt
   
   # Note: For running the standalone LangGraph components
   pip install langgraph
   ```

### Running the API (Recommendations)
```bash
uvicorn app.main:app --reload
```
Test endpoints safely via the Swagger interface: `http://127.0.0.1:8000/docs`.

### Running the Multi-Agent Flow (Prototype)
```bash
cd project
python main.py
```

---

## 🔌 API Documentation (Usage & Payloads)

### `POST /get-schemes`

**Sample User Profile Request**:
```json
{
  "age": 25,
  "income": 150000,
  "occupation": "farmer",
  "gender": "male",
  "state": "Uttar Pradesh"
}
```

**Expected Winner-Level Response**:
```json
[
  {
    "scheme_name": "PM Kisan Samman Nidhi",
    "eligible": true,
    "confidence_score": 1.0,
    "match_reason": "Strong Match: User perfectly fits criteria. Matched occupation, Matched income",
    "benefits": "₹6000/year - Financial assistance to small and marginal farmers",
    "application_link": "https://pmkisan.gov.in",
    "category": "Agriculture",
    "documents_required": [
      "Aadhaar Card",
      "Bank Account Details",
      "Land Ownership Records"
    ],
    "match_type": "Full",
    "priority_tag": "Standard"
  }
]
```

---

## 📈 Scalability Story (Production Roadmap)
While currently optimized for local hackathon deployment via FAISS CPU architectures, this backend is conceptually bound for massive scaling. 
**We can infinitely scale this recommendation engine by migrating the local FAISS vector arrays to distributed vector databases like Pinecone or Weaviate, whilst securely deploying the stateless FastAPI nodes horizontally behind load balancers. Integrating the multi-agent capabilities built in `/project` opens up possibilities for autonomous, conversational insights complementing our real-time API.**
