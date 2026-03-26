# 🤖 AI-Powered Intelligent Customer Service Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Orchestration-purple.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

End-to-end customer service automation using LLM agents with intent classification, knowledge base RAG, multi-turn conversation management, sentiment-aware responses, intelligent escalation routing, and ticket analytics — built with **LangChain** and **LangGraph**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Customer Service AI Platform                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────┐    ┌──────────────────────────────────────────────┐    │
│  │ Customer  │───▶│            FastAPI Gateway                   │    │
│  │  Input    │    │  /chat  /classify  /sentiment  /escalate     │    │
│  └──────────┘    └────────────────┬─────────────────────────────┘    │
│                                   │                                   │
│                    ┌──────────────▼──────────────┐                   │
│                    │    Intent Classifier Agent    │                   │
│                    │  (Few-shot LLM Classification)│                   │
│                    └──────────────┬──────────────┘                   │
│                                   │                                   │
│         ┌─────────────────────────┼─────────────────────────┐       │
│         ▼                         ▼                         ▼       │
│  ┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐    │
│  │  Sentiment   │   │  Conversation    │   │   Escalation     │    │
│  │  Analyzer    │   │  Agent (RAG)     │   │   Router         │    │
│  │              │   │                  │   │                  │    │
│  │ • Emotion    │   │ • Multi-turn     │   │ • Priority Score │    │
│  │ • Tone Adj.  │   │ • Context Mgmt  │   │ • Dept Routing   │    │
│  │ • Trajectory │   │ • KB Retrieval   │   │ • Summary Gen    │    │
│  └──────────────┘   └────────┬─────────┘   └──────────────────┘    │
│                              │                                       │
│                    ┌─────────▼──────────┐                           │
│                    │   ChromaDB (RAG)    │                           │
│                    │  Knowledge Base     │                           │
│                    │  • FAQs             │                           │
│                    │  • Product Docs     │                           │
│                    │  • Policies         │                           │
│                    │  • Troubleshooting  │                           │
│                    └────────────────────┘                            │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Ticket Analyzer & Analytics Engine               │    │
│  │  • Auto-categorization  • Root cause clustering              │    │
│  │  • Resolution prediction • Trend detection • Reporting       │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Streamlit Dashboard                              │    │
│  │  • Live Chat Simulator    • Agent Dashboard                  │    │
│  │  • Sentiment Tracking     • Escalation Queue                 │    │
│  │  • Ticket Analytics       • Knowledge Base Explorer          │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Features

### 🎯 Intent Classification
- Classifies customer queries into: Billing, Technical Support, Account Management, Feature Request, Complaint, General Inquiry
- Few-shot prompting for high accuracy
- Returns confidence scores and sub-categories

### 💬 Multi-Turn Conversation Management
- RAG-powered responses grounded in company knowledge base
- Maintains full conversation context and history
- Follows configurable company tone and style guidelines
- Gracefully handles ambiguity and knows when to say "I don't know"

### 😊 Sentiment Analysis
- Real-time emotion detection (frustrated, neutral, satisfied, angry)
- Dynamic tone adjustment based on detected sentiment
- Empathy-first responses for negative sentiment
- Tracks sentiment trajectory across the conversation

### 🚨 Intelligent Escalation Routing
- Trigger-based escalation (repeated issues, high frustration, complex technical, billing disputes)
- Routes to appropriate department (Billing, Technical L2, Management)
- Auto-generates escalation summaries for human agents
- Priority scoring: P1 (Critical) → P4 (Low)

### 📊 Ticket Analytics
- Automatic ticket categorization
- Root cause clustering and trend detection
- Resolution time prediction
- Weekly/monthly analytics reports

### 🖥️ Interactive Dashboard
- Live chat simulator for testing
- Real-time agent dashboard
- Sentiment tracking visualizations
- Escalation queue management
- Ticket analytics with charts

---

## Project Structure

```
customer-service-ai/
├── README.md
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .gitignore
├── data/
│   └── knowledge_base/
├── src/
│   ├── __init__.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   ├── kb_loader.py
│   │   └── sample_kb.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py
│   │   ├── conversation_agent.py
│   │   ├── sentiment_analyzer.py
│   │   ├── escalation_router.py
│   │   └── ticket_analyzer.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── app.py
│   └── dashboard/
│       ├── __init__.py
│       └── app.py
```

---

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd customer-service-ai

# Install dependencies
make install

# Set up environment
cp .env.example .env
# Add your OpenAI API key to .env

# Generate sample knowledge base
make generate-kb

# Load knowledge base into ChromaDB
make load-kb

# Start FastAPI server
make api

# Start Streamlit dashboard (separate terminal)
make dashboard
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Handle customer message (multi-turn) |
| POST | `/classify` | Classify customer intent |
| POST | `/sentiment` | Analyze message sentiment |
| POST | `/escalate` | Evaluate escalation need |
| POST | `/tickets/analyze` | Analyze a batch of tickets |
| GET | `/conversation/{id}` | Get conversation history |
| GET | `/health` | Health check |

---

## Tech Stack

- **LLM Framework**: LangChain + LangGraph
- **LLM Provider**: OpenAI GPT-4
- **Vector Store**: ChromaDB
- **Embeddings**: sentence-transformers / OpenAI
- **API**: FastAPI + Uvicorn
- **Dashboard**: Streamlit
- **Containerization**: Docker + Docker Compose

---

## Author

**Naresh Sampangi**

---

## License

This project is licensed under the MIT License.
