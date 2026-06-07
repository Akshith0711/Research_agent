"""
AI Research Agent with:
- LLM-based Router
- RAG (FAISS + Embeddings)
- Web Search (Tavily)
- Intelligent fallback mechanism
"""

import os
from tavily import TavilyClient
from langgraph.graph import StateGraph
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader


# ────────────────────────────────────────────────────────────────
# 📚 Build Vector Store
# ────────────────────────────────────────────────────────────────
def build_vectorstore(pdf_paths: list[str]) -> FAISS:

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
# 🔍 Retrieve from KB
# ────────────────────────────────────────────────────────────────
def retrieve_from_kb(vectorstore: FAISS, query: str, k: int = 4):

    docs_and_scores = vectorstore.similarity_search_with_score(query, k=k)

    if not docs_and_scores:
        return "", False

    filtered_docs = []

    for doc, score in docs_and_scores:
        if score < 1.2:
            filtered_docs.append(doc.page_content)

    if not filtered_docs:
        return "", False

    context = "\n\n".join(filtered_docs)
    return context, True


# ────────────────────────────────────────────────────────────────
# 🧠 Build LangGraph Agent
# ────────────────────────────────────────────────────────────────
def build_graph(vectorstore: FAISS = None):

    # ✅ LLM initialized ONLY inside function
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    search_client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY")
    )

    # ── Router Node
    def router_node(state):
        query = state["query"]

        prompt = f"""
Decide the best source:
- rag → internal/company knowledge
- web → general/latest info
- both → combination

Query: {query}
Answer ONLY: rag / web / both
"""

        decision = llm.invoke(prompt).content.lower().strip()

        if "both" in decision:
            route = "both"
        elif "rag" in decision:
            route = "rag"
        else:
            route = "web"

        return {**state, "route": route}

    # ── RAG Node
    def rag_node(state):
        query = state["query"]
        route = state.get("route", "web")

        kb_context = ""
        used_rag = False

        if vectorstore and route in ["rag", "both"]:
            kb_context, used_rag = retrieve_from_kb(vectorstore, query)

        return {**state, "kb_context": kb_context, "used_rag": used_rag}

    # ── Web Node
    def search_node(state):
        route = state.get("route", "web")

        if route == "rag" and state.get("used_rag"):
            return {**state, "documents": []}

        results = search_client.search(query=state["query"], search_depth="advanced")

        return {**state, "documents": results["results"]}

    # ── Summary Node
    def summarize_node(state):
        if state.get("used_rag"):
            return {**state, "summary": state["kb_context"]}

        docs = state.get("documents", [])

        if docs:
            content = " ".join([doc["content"] for doc in docs[:5]])
            summary = llm.invoke(f"Summarize:\n{content}")
            return {**state, "summary": summary.content}

        return {**state, "summary": "No relevant information found."}

    # ── Answer Node
    def answer_node(state):
        prompt = f"""
Answer clearly.

Question: {state['query']}
Context: {state['summary']}
"""
        answer = llm.invoke(prompt)
        return {**state, "final_answer": answer.content}

    # ── Graph
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