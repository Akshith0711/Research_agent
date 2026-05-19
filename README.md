# 🔍 AI Research Agent

A simple AI-powered research assistant that can search the web, summarize information, and generate answers using a structured agent workflow.

---

## 🚀 Features

- 🔍 Web search using Tavily API  
- 🧠 Summarization using LLM  
- ✍️ Answer generation based on retrieved data  
- 💬 Chat-style interface using Streamlit  

---

## 🛠️ Tech Stack

- Python  
- LangGraph  
- Groq LLM  
- Tavily API  
- Streamlit  

---

## ⚙️ How It Works

The system follows a step-by-step pipeline:

1. User enters a query  
2. Agent searches the web using Tavily  
3. Retrieved content is summarized  
4. Final answer is generated using LLM  

---

## 📂 Project Structure
.
├── app.py # Streamlit UI
├── agent.py # LangGraph agent logic
├── requirements.txt
└── README.md
---

## ▶️ Installation & Setup

1. Clone the repository:

   git clone https://github.com/your-username/Research_agent.git
   cd Research_agent

2. Create a virtual environment:
    python -m venv venv
    venv\Scripts\activate # Windows

3. Install dependencies:

    pip install -r requirements.txt

4. Add your API keys in `.env` file:

   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key
---

## ▶️ Run the App
   streamlit run app.py

---

## 💡 Key Learnings

- Built a multi-step AI agent using LangGraph  
- Integrated external APIs for real-time data  
- Handled state management across agent nodes  
- Designed a simple UI using Streamlit  

---

## 🚀 Future Improvements

- Add RAG (Retrieval-Augmented Generation)  
- Add memory for follow-up questions  
- Improve UI and user experience  

---

## 📌 Note

This is a learning project to understand how agent-based AI systems work.

---

## 📬 Feedback

Feel free to suggest improvements or connect with me!
