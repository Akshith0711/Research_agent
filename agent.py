"""
AI Research Agent with:
- LLM-based Router
- RAG (FAISS + Embeddings)
- Web Search (Tavily)
- Intelligent fallback mechanism

Author: Akshith Reddy
"""

import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

# ────────────────────────────────────────────────────────────────
# 🔐 Load Environment Variables
# ────────────────────────────────────────────────────────────────
load_dotenv()

# ────────────────────────────────────────────────────────────────
# 🤖 LLM Configuration
# ────────────────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")  # NEVER hardcode keys
)

# ────────────────────────────────────────────────────────────────
# 🌐 Web Search Client
# ────────────────────────────────────────────────────────────────
search_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# ────────────────────────────────────────────────────────────────
# 📚 RAG: Build Vector Store from PDFs
# ────────────────────────────────────────────────────────────────
def build_vectorstore(pdf_paths: list[str]) -> FAISS:
    """
    Loads PDFs → splits into chunks → creates embeddings → stores in FAISS.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    documents = []

    for path in pdf_paths:
        loader = PyPDFLoader(path)
        pages = loader.load()
        chunks = splitter.split_documents(pages)
        documents.extend(chunks)

    return FAISS.from_documents(documents, embeddings)


# ────────────────────────────────────────────────────────────────
# 🔍 RAG Retrieval with Relevance Filtering
# ────────────────────────────────────────────────────────────────
def retrieve_from_kb(vectorstore: FAISS, query: str, k: int = 4):
    """
    Performs similarity search and filters irrelevant results
    using score threshold.

    Returns:
        context (str)
        is_relevant (bool)
    """

    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)

    if not docs_and_scores:
        return "", False

    filtered_docs = []

    for doc, score in docs_and_scores:
        # Lower score = better semantic match
        if score < 1.2:
            filtered_docs.append(doc.page_content)

    if not filtered_docs:
        return "", False

    context = "\n\n".join(filtered_docs)
    return context, True


# ────────────────────────────────────────────────────────────────
# 🧠 LangGraph Agent Builder
# ────────────────────────────────────────────────────────────────
def build_graph(vectorstore: FAISS = None):
    """
    Builds an AI agent with:
    - Router (LLM decision)
    - RAG retrieval
    - Web search fallback
    - Answer generation
    """

    # ── Router Node ───────────────────────────────────────────
    def router_node(state):
        """Decides whether to use RAG, Web, or Both."""

        query = state["query"]

        prompt = f"""
Decide the best source:

- "rag" → internal/company knowledge
- "web" → general/latest information
- "both" → combination of both

Query: {query}

Answer ONLY one word: rag / web / both
"""

        decision = llm.invoke(prompt).content.lower().strip()

        if "both" in decision:
            route = "both"
        elif "rag" in decision:
            route = "rag"
        else:
            route = "web"

        return {**state, "route": route}

    # ── RAG Node ──────────────────────────────────────────────
    def rag_node(state):
        """Retrieves relevant information from knowledge base."""

        query = state["query"]
        route = state.get("route", "web")

        kb_context = ""
        used_rag = False

        if vectorstore and route in ["rag", "both"]:
            kb_context, used_rag = retrieve_from_kb(vectorstore, query)

        return {
            **state,
            "kb_context": kb_context,
            "used_rag": used_rag
        }

    # ── Web Search Node ───────────────────────────────────────
    def search_node(state):
        """Fetches real-time data from the web if needed."""

        route = state.get("route", "web")

        # Skip web if RAG-only and successful
        if route == "rag" and state.get("used_rag"):
            return {**state, "documents": []}

        query = state["query"]
        results = search_client.search(query=query, search_depth="advanced")

        return {
            **state,
            "documents": results["results"]
        }

    # ── Summarization Node ────────────────────────────────────
    def summarize_node(state):
        """Summarizes retrieved information."""

        kb_context = state.get("kb_context", "")
        docs = state.get("documents", [])
        used_rag = state.get("used_rag", False)

        # Prefer KB if relevant
        if used_rag and kb_context:
            return {**state, "summary": kb_context}

        # Otherwise summarize web results
        if docs:
            content = " ".join([doc["content"] for doc in docs[:5]])
            prompt = f"Summarize this clearly:\n{content}"
            summary = llm.invoke(prompt)

            return {**state, "summary": summary.content}

        return {
            **state,
            "summary": "No relevant information found."
        }

    # ── Answer Node ───────────────────────────────────────────
    def answer_node(state):
        """Generates final answer using LLM."""

        query = state["query"]
        summary = state["summary"]
        route = state.get("route", "web")

        source_hint = {
            "rag": "Use internal knowledge base.",
            "web": "Use web search data.",
            "both": "Use both knowledge base and web data."
        }.get(route)

        prompt = f"""
Answer clearly and in detail.

{source_hint}

Question: {query}
Context: {summary}
"""

        answer = llm.invoke(prompt)

        return {
            **state,
            "final_answer": answer.content
        }

    # ── Graph Construction ─────────────────────────────────────
    builder = StateGraph(dict)

    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("search", search_node)
    builder.add_node("summarize", summarize_node)
    builder.add_node("answer", answer_node)

    builder.set_entry_point("router")

    builder.add_edge("router", "rag")
    builder.add_edge("rag", "search")
    builder.add_edge("search", "summarize")
    builder.add_edge("summarize", "answer")

    return builder.compile()


# ────────────────────────────────────────────────────────────────
# 🚀 Default Graph (Web-only mode)
# ────────────────────────────────────────────────────────────────
graph = build_graph(vectorstore=None)