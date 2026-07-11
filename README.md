# ai-hcp-crm
AI-First HCP CRM with LangGraph and Groq

# AI-First HCP CRM

An AI-powered CRM system for Healthcare Professionals (HCPs) with LangGraph agent and Groq LLM integration.

## 🚀 Features

- **Log HCP Interactions** via structured form or AI chat
- **Voice Recording** with AI summarization
- **LangGraph Agent** with 7 tools:
  1. Log Interaction
  2. Edit Interaction
  3. Summarize Interaction
  4. Extract Interaction Details
  5. Generate Follow-up Recommendations
  6. Search HCP
  7. Get Interaction History
- **AI Assistant** powered by Groq (llama-3.1-8b-instant)
- **Redux** state management
- **FastAPI** backend with SQLite/PostgreSQL

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Redux Toolkit, Material UI |
| Backend | FastAPI, SQLAlchemy |
| AI Agent | LangGraph, LangChain |
| LLM | Groq (llama-3.1-8b-instant) |
| Database | SQLite (dev) / PostgreSQL (prod) |

## 📦 Installation

### Prerequisites
- Node.js 18+
- Python 3.9+
- Groq API Key (get from https://console.groq.com)

### Backend Setup
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add GROQ_API_KEY
python init_db.py
python run.py
