import streamlit as st
import tempfile
import os
from agent import build_graph, build_vectorstore

# ────────────────────────────────────────────────────────────────
# ⚙️ Page Config
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Research Agent")
st.caption("Chat with AI using Web + Knowledge Base")

# ────────────────────────────────────────────────────────────────
# 🎨 Global Styling (Clean + Professional)
# ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.chat-answer {
    font-size: 17px;
    line-height: 1.7;
}

.chat-user {
    font-size: 15px;
    font-weight: 500;
}

.section-title {
    font-size: 14px;
    color: gray;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# 🧠 Session State Initialization
# ────────────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = build_graph(vectorstore=None)

if "kb_active" not in st.session_state:
    st.session_state.kb_active = False

if "uploaded_names" not in st.session_state:
    st.session_state.uploaded_names = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────────────────────
# 📚 Sidebar — Knowledge Base
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Knowledge Base")

    uploaded_pdfs = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Build Knowledge Base", use_container_width=True):
        if not uploaded_pdfs:
            st.error("Upload at least one PDF.")
        else:
            with st.spinner("Processing PDFs..."):
                temp_paths = []

                for pdf in uploaded_pdfs:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
                        f.write(pdf.read())
                        temp_paths.append(f.name)

                try:
                    vectorstore = build_vectorstore(temp_paths)
                    st.session_state.graph = build_graph(vectorstore=vectorstore)
                    st.session_state.kb_active = True
                    st.session_state.uploaded_names = [p.name for p in uploaded_pdfs]

                    st.success("Knowledge Base Ready")

                except Exception as e:
                    st.error(f"Error: {e}")

                finally:
                    for path in temp_paths:
                        os.unlink(path)

    st.divider()

    if st.session_state.kb_active:
        st.markdown("**Status:** 🟢 Active")
        for name in st.session_state.uploaded_names:
            st.write(f"📄 {name}")

        if st.button("Reset Knowledge Base"):
            st.session_state.graph = build_graph(vectorstore=None)
            st.session_state.kb_active = False
            st.session_state.uploaded_names = []
            st.rerun()
    else:
        st.markdown("**Status:** 🔴 Web Mode")

    st.divider()
    st.caption("Upload documents to enable knowledge-based answers")

# ────────────────────────────────────────────────────────────────
# 💬 Chat Interface
# ────────────────────────────────────────────────────────────────

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"<div class='chat-user'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-answer'>{message['content']}</div>", unsafe_allow_html=True)

# User input
user_query = st.chat_input("Ask anything...")

if user_query:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(f"<div class='chat-user'>{user_query}</div>", unsafe_allow_html=True)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            result = st.session_state.graph.invoke({"query": user_query})

            answer = result["final_answer"]
            summary = result["summary"]

            # 🔹 Source indicator (clean)
            if result.get("used_rag"):
                st.markdown("📚 *Knowledge Base*")
            else:
                st.markdown("🌐 *Web Search*")

            st.markdown("---")

            # 🔹 Answer (primary focus)
            st.markdown("<div class='section-title'>Answer</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-answer'>{answer}</div>", unsafe_allow_html=True)

            # 🔹 Summary (secondary)
            with st.expander("🧠 Summary"):
                st.markdown(summary)

            # 🔹 Sources (tertiary)
            with st.expander("📚 Sources"):
                if result.get("used_rag"):
                    st.write("From uploaded documents")
                else:
                    for doc in result.get("documents", [])[:3]:
                        st.write(doc["url"])

    # Store assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })