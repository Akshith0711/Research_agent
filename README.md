# 🤖 AI Research Agent

An AI-powered Research Assistant that combines **Retrieval-Augmented Generation (RAG)**, **Real-Time Web Search**, and **LLM-based Routing** to deliver accurate, context-aware responses.

The system intelligently determines whether a query should be answered using an uploaded knowledge base, live web search results, or a combination of both.

---

## 🚀 Live Demo

**Live Application:** [Add Your Render URL]

**GitHub Repository:** [Add Your Repository URL]

---

## 📖 Overview

AI Research Agent is an end-to-end Generative AI application designed to provide reliable answers by combining:

* 📚 Knowledge Base Retrieval (RAG)
* 🌐 Real-Time Web Search
* 🧠 Intelligent Query Routing
* ⚡ Fast LLM Inference

Unlike traditional chatbots, the system dynamically selects the most relevant information source before generating a response.

---

## ✨ Features

### 📚 Knowledge Base Search

* Upload one or multiple PDF documents
* Automatic document chunking and indexing
* Semantic retrieval using FAISS Vector Database
* Context-aware question answering

### 🌐 Real-Time Web Search

* Live web search powered by Tavily API
* Access to current and up-to-date information
* Automatic web content summarization

### 🧠 Intelligent Routing Agent

The system automatically decides whether to:

* Use Knowledge Base Retrieval (RAG)
* Use Web Search
* Use Both Sources

### 💬 Interactive Chat Interface

* Streamlit-based conversational UI
* Chat history support
* Source-aware responses
* PDF upload and management

### ⚡ Fast AI Responses

* Powered by Groq's Llama 3.1 model
* Low-latency answer generation

---

## 🏗️ System Architecture

```text
User Query
     │
     ▼
LLM Router
     │
 ┌───┴─────────────┐
 │                 │
 ▼                 ▼
RAG          Web Search
(FAISS)       (Tavily)
 │                 │
 └── Context Fusion ──┘
           │
           ▼
       Groq LLM
           │
           ▼
     Final Answer
```

---

## 🛠️ Tech Stack

### AI & LLM

* Groq (Llama 3.1 8B Instant)
* Google Gemini Embeddings

### Frameworks

* LangGraph
* LangChain

### Retrieval

* FAISS Vector Database

### Search

* Tavily Search API

### Frontend

* Streamlit

### Backend

* Python

### Utilities

* PyPDF
* Python Dotenv

---

## ⚙️ Workflow

1. User submits a query.
2. Router Agent analyzes query intent.
3. System determines the best information source:

   * Knowledge Base
   * Web Search
   * Hybrid Retrieval
4. Relevant context is retrieved.
5. Information is summarized.
6. Groq LLM generates the final response.
7. Answer is displayed through the Streamlit interface.

---

## 📂 Project Structure

```text
Research_Agent/
│
├── app.py                 # Streamlit UI
├── agent.py               # LangGraph Workflow
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone <repository-url>
cd Research_Agent
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Run Application

```bash
streamlit run app.py
```

---

## 🎯 Use Cases

* Research Assistance
* Enterprise Knowledge Retrieval
* Document Question Answering
* AI-Powered Search Systems
* Internal Knowledge Base Assistants
* Educational Learning Platforms

---

## 📸 Screenshots

Add screenshots of:

* Home Page
* PDF Upload Interface
* Knowledge Base Response
* Web Search Response
* Hybrid Search Response

---

## 🚀 Future Enhancements

* Conversational Memory
* Multi-Agent Architecture
* Source Citations
* Docker Deployment
* Cloud Vector Databases
* User Authentication
* Multi-Document Knowledge Bases

---

## 👨‍💻 Author

**Akshith Reddy**

Aspiring AI Engineer focused on:

* Generative AI
* Agentic AI Systems
* Retrieval-Augmented Generation (RAG)
* Large Language Models
* Applied Machine Learning

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.
