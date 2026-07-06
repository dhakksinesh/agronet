# 🌾 AgroNet

> **Multi-Agent AI Powered Smart Crop Advisory System for Indian Agriculture**

AgroNet is an Agentic AI platform that helps Indian farmers make informed farming decisions by coordinating multiple specialized AI agents. The system combines Retrieval-Augmented Generation (RAG), live weather intelligence, and trusted agricultural knowledge to generate personalized, explainable, and evidence-based recommendations.

---

<a name="table-of-contents"></a>
## 📋 Table of Contents

- [Key Features](#key-features)
- [Live Demo](#live-demo)
- [How It Works](#how-it-works)
- [Multi-Agent Architecture](#multi-agent-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Demo Scenario](#demo-scenario)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Technology Stack](#technology-stack)
- [Sources](#sources)

---

<a name="key-features"></a>
## ✨ Key Features

### Multi-Agent Reasoning Pipeline
Nine specialized AI agents collaborate in sequence to understand the farmer's query, retrieve relevant context, reason about the problem, and generate validated recommendations.

### Dual Crew Architecture
Two CrewAI crews handle different query types:
- **Full Advisory Crew** — 9 agents for comprehensive structured reports with weather, pests, schemes, and detailed action plans
- **Quick Answer Crew** — 5 agents for direct 2-4 sentence answers to simple queries (water amounts, fertilizer ratios, pest treatments)

### Off-Topic Guard
Natural language classifier detects non-farming queries and politely redirects, preventing wasted LLM calls and ensuring the system stays focused on agriculture.

### Smart Follow-Up Handling
Conversation context is passed between exchanges — follow-ups like "what about fertilizer?" or "can I do it in the evening?" are correctly understood in context.

### RAG-Powered Knowledge Base
Pinecone vector store indexes agricultural PDFs (ICAR guides, TNAU bulletins, government schemes) and retrieves relevant passages to ground all recommendations.

### Live Weather Integration
7-day weather forecasts from Open-Meteo are fetched in real-time per district, feeding temperature, rainfall, humidity, and wind data into the advisory pipeline.

### Dashboard & Analytics
Streamlit dashboard shows current season info, crop calendar, weather snapshot, and per-farm query history with search and export.

### Multi-Farm Profile Management
Create, switch, edit, and delete multiple farm profiles — each with its own state, district, crop, and soil type.

---

<a name="live-demo"></a>
## 🚀 Live Demo

Try AgroNet live at: [**AgroNet**](https://agronet-dkxy.streamlit.app/)

---

<a name="how-it-works"></a>
## ⚙️ How It Works

```
Farmer Query
    │
    ├─► Greeting? ──► Welcome message
    │
    ├─► Off-topic? ──► Polite redirect (keyword + LLM classifier)
    │
    └─► Farming Query
            │
            ├─► Simple query? (water, fertilizer, pest, weather)
            │       └─► Quick Answer Crew (5 agents, 2-4 sentence reply)
            │
            └─► Complex query?
                    └─► Full Advisory Crew (9 agents, structured report)
                            │
                            ├─► 1. Farmer Profile Agent — Understands the query
                            ├─► 2. Weather Intelligence Agent — Fetches live forecast
                            ├─► 3. Knowledge Retrieval Agent — RAG search
                            ├─► 4. Crop Advisory Agent — Irrigation + fertilizer
                            ├─► 5. Disease & Pest Agent — Risk assessment
                            ├─► 6. Government Scheme Agent — Scheme eligibility
                            ├─► 7. Recommendation Agent — Prioritized action plan
                            ├─► 8. Evaluation Agent — Validates all outputs
                            └─► 9. Report Generator Agent — Formats final report
```

For a detailed breakdown of agents, data flow, and system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

<a name="multi-agent-architecture"></a>
## 🤖 Multi-Agent Architecture

| Agent | Role | Tools |
|-------|------|-------|
| **Farmer Profile Agent** | Extracts intent, understands context from conversation history | LLM |
| **Weather Intelligence Agent** | Fetches 7-day forecast for farmer's district | Open-Meteo API |
| **Knowledge Retrieval Agent** | Searches RAG vector store for relevant documents | Pinecone |
| **Crop Advisory Agent** | Generates irrigation, fertilizer, and management recommendations | LLM |
| **Disease & Pest Agent** | Assesses pest/disease risk and recommends treatments | LLM |
| **Government Scheme Agent** | Identifies eligible subsidies and schemes | RAG tool |
| **Recommendation Agent** | Synthesizes all outputs into prioritized action plan | LLM |
| **Evaluation Agent** | Validates accuracy, consistency, and safety | LLM |
| **Report Generator Agent** | Formats final advisory into readable report | LLM |

---

<a name="prerequisites"></a>
## ✅ Prerequisites

- **Python 3.13+** installed
- **pip** package manager
- **Pinecone API key** ([get one here](https://www.pinecone.io/))
- **OpenRouter API key** ([get one here](https://openrouter.ai/keys))
- **Git** (for cloning)

---

<a name="installation"></a>
## 📦 Installation

### Clone

```bash
git clone https://github.com/dhakksinesh/agronet.git
cd agronet
```

### Virtual Environment (recommended)

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Set Up Environment

**Windows (cmd):**
```cmd
copy .env.example .env
```

**Mac / Linux:**
```bash
cp .env.example .env
```

Then open `.env` in a text editor and fill in your API keys (see [Configuration](#configuration)).

---

<a name="configuration"></a>
## 🔧 Configuration

Create a `.env` file in the project root:

```env
# Pinecone Configuration
# Get your API key from: https://www.pinecone.io/
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=agronet
PINECONE_EMBEDDING_MODEL=llama-text-embed-v2
PINECONE_EMBEDDING_DIM=1024

# OpenRouter Configuration (LLM Gateway)
# Get your API key from: https://openrouter.ai/keys
# Choose a compatible model from: https://openrouter.ai/models
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=your_openrouter_model_here

# CrewAI Tracing
CREWAI_TRACING_ENABLED=true

# Weather API Configuration (Open-Meteo)
WEATHER_API_BASE=https://api.open-meteo.com/v1/forecast
```

| Variable | Required | Get It |
|----------|----------|--------|
| `PINECONE_API_KEY` | Yes | [pinecone.io](https://www.pinecone.io/) |
| `OPENROUTER_API_KEY` | Yes | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `OPENROUTER_MODEL` | Yes | [openrouter.ai/models](https://openrouter.ai/models) |
| `WEATHER_API_BASE` | No | Built-in |

---

<a name="usage"></a>
## 🎯 Usage

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`.

### First-Time Setup

1. **Create a farm profile** — Go to the Profiles tab, select your state, district, crop type, crop, and soil type
2. **Seed the database** (one-time) — The database auto-initializes with states, districts, crops, and soil types
3. **Add PDF documents** — Place agricultural PDFs in `data/` for RAG ingestion (automatic on first run)
4. **Start chatting** — Ask about irrigation, fertilizer, pests, weather, or government schemes

---

<a name="project-structure"></a>
## 📁 Project Structure

<details>
<summary>Click to expand project tree</summary>

```
agronet/
├── app.py                   # Streamlit web interface (main entry point)
├── config/                  # Configuration and LLM setup
│   ├── __init__.py          # Environment config, API keys, validation
│   └── llm.py               # CrewAI LLM factory with hosted_vllm prefix
├── agents/                  # CrewAI agent definitions
│   ├── farmer_profile.py
│   ├── weather_intelligence.py
│   ├── knowledge_retrieval.py
│   ├── crop_advisory.py
│   ├── disease_pest.py
│   ├── government_scheme.py
│   ├── recommendation.py
│   ├── evaluation.py
│   └── report_generator.py
├── crews/                   # Crew orchestration
│   └── __init__.py          # agri_crew (full) + simple_crew (quick)
├── tasks/                   # Task definitions with context chaining
│   ├── profile_task.py
│   ├── weather_task.py
│   ├── knowledge_task.py
│   ├── crop_task.py
│   ├── disease_task.py
│   ├── government_task.py
│   ├── recommendation_task.py
│   ├── evaluation_task.py
│   ├── report_task.py
│   └── simple_report_task.py
├── tools/                    # Utility tools
│   ├── weather.py            # Open-Meteo weather data + geocoding
│   └── government_schemes.py # RAG-based scheme retrieval
├── rag/                      # RAG integration
│   └── retriever.py          # Pinecone vector store, embedding, ingestion
├── database/                 # SQLite database layer
│   ├── __init__.py           # CRUD operations, query functions
│   ├── seed_all.py           # Run all seed scripts in sequence
│   ├── seed_states.py        # 36 Indian states/UTs
│   ├── seed_districts.py     # District data
│   ├── seed_crops.py         # Crop types and commodities
│   └── seed_soils.py         # Soil types
├── utils/                    # Helper utilities
│   └── logging_config.py     # Centralized logging (console + file)
├── data/                     # Agricultural PDFs for RAG
│   ├── README.md             # Placeholder with source suggestions
│   ├── Generic_Crop_Growing_Guidelines_Handbook_India.pdf
│   ├── Generic_Fertilizer_Handbook_India.pdf
│   ├── Generic_Pest_Disease_Management_Handbook_India.pdf
│   ├── Indian_Agriculture_Guidelines_Handbook_2025_2026.pdf
│   └── Indian_Government_Agriculture_Schemes_Handbook.pdf
├── .gitignore
├── requirements.txt
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

</details>

---

<a name="demo-scenario"></a>
## 🧪 Demo Scenario

**Input**: Tamil Nadu, Chennai, Green Peas, Alluvial Soil

**Query**: "How much water should I pour every day?"

**Output**: Weather summary, irrigation recommendation (25mm every 3-4 days), fertilizer plan, pest alerts, eligible schemes (PMKSY, NHM, RKVY, PMFBY), and prioritized action plan — all in a structured advisory report.

---

<a name="troubleshooting"></a>
## 🔍 Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError` | Missing dependency | Run `pip install -r requirements.txt` |
| API key errors | Missing or invalid `.env` | Copy `.env.example` to `.env` and fill in keys |
| Pinecone index errors | Wrong region or index name | Ensure `PINECONE_INDEX_NAME` matches your Pinecone console |
| CrewAI agent timeout | LLM API rate limited | Wait a minute and retry, or switch to a faster model |
| No RAG results | No PDFs in `data/` | Add agricultural PDFs to the `data/` folder |
| `streamlit` command not found | Virtual env not activated | Activate your venv (`venv\Scripts\activate` or `source venv/bin/activate`) |
| Dashboard widgets blank | LLM call failure | Check `logs/agronet.log` for details |

---

<a name="development"></a>
## 👨‍💻 Development

### Adding New Agents

1. Create agent file in `agents/` with `from crewai import Agent`
2. Add task in `tasks/` with context references to upstream tasks
3. Register both in `crews/__init__.py` and `tasks/__init__.py`
4. Wire task context in the sequential pipeline

### Model Configuration

The `hosted_vllm/` prefix is automatically added for models containing `/` (e.g., `openai/gpt-oss-120b` → `hosted_vllm/openai/gpt-oss-120b`). This forces CrewAI's `OpenAICompatibleCompletion` provider which preserves the full model name in API requests.

---

<a name="technology-stack"></a>
## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.13 |
| UI | Streamlit |
| Multi-Agent Framework | CrewAI 1.15.1 + LangChain + LiteLLM 1.91.0 |
| LLM Gateway | OpenRouter |
| RAG Framework | LlamaIndex |
| Vector DB | Pinecone |
| Embeddings | llama-text-embed-v2 |
| Keyword Search | BM25 (in-memory index) |
| Score Fusion | Reciprocal Rank Fusion (RRF) |
| Database | SQLite |
| Weather API | Open-Meteo |
| PDF Processing | PyMuPDF |
| Validation | Pydantic v2 |

---

<a name="sources"></a>
## 📚 Sources

### Agricultural PDFs for RAG

#### Synthetic Test Data (included in repository)

The repository ships with 5 synthetic PDFs generated using ChatGPT + Wikipedia for testing:

- [`Indian_Agriculture_Guidelines_Handbook_2025_2026.pdf`](data/Indian_Agriculture_Guidelines_Handbook_2025_2026.pdf)
- [`Generic_Crop_Growing_Guidelines_Handbook_India.pdf`](data/Generic_Crop_Growing_Guidelines_Handbook_India.pdf)
- [`Generic_Fertilizer_Handbook_India.pdf`](data/Generic_Fertilizer_Handbook_India.pdf)
- [`Generic_Pest_Disease_Management_Handbook_India.pdf`](data/Generic_Pest_Disease_Management_Handbook_India.pdf)
- [`Indian_Government_Agriculture_Schemes_Handbook.pdf`](data/Indian_Government_Agriculture_Schemes_Handbook.pdf)

#### Recommended Sources (curate manually for production)

- ICAR Crop Production Guides
- TNAU Extension Publications
- Ministry of Agriculture Guidelines
- Krishi Vigyan Kendra Advisories
- PM-KISAN / PMFBY Scheme Documents
- Fertilizer Recommendation Manuals
- Integrated Pest Management Documents

### Database Reference Data

| Dataset | Source |
|---------|--------|
| States & Districts | [igod.gov.in/sg/district/states](https://igod.gov.in/sg/district/states) |
| Crops & Commodities | [agmarknet.gov.in](https://agmarknet.gov.in/home) |
| Soil Types | [Wikipedia — Major soil deposits of India](https://en.wikipedia.org/wiki/Major_soil_deposits_of_India) |
