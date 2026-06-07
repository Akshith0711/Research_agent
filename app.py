# ────────────────────────────────────────────────────────────────
# 🔐 Load Environment FIRST
# ────────────────────────────────────────────────────────────────
from dotenv import load_dotenv
import os

load_dotenv(override=True)  # 🔥 FIX: force correct env usage

# ────────────────────────────────────────────────────────────────
# 📦 Imports
# ────────────────────────────────────────────────────────────────
import streamlit as st
import tempfile

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
# 🎨 Styling
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
# 🧠 Session State
# ────────────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    st.session_state.graph = None  # 🔥 FIX

if "kb_active" not in st.session_state:
    st.session_state.kb_active = False

if "uploaded_names" not in st.session_state:
    st.session_state.uploaded_names = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ────────────────────────────────────────────────────────────────
# 📚 Sidebar (Knowledge Base)
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
                    st.error(f"Error building KB: {e}")

                finally:
                    for path in temp_paths:
                        os.unlink(path)

    st.divider()

    if st.session_state.kb_active:
        st.markdown("**Status:** 🟢 Active")
        for name in st.session_state.uploaded_names:
            st.write(f"📄 {name}")

        if st.button("Reset Knowledge Base"):
            st.session_state.graph = None
            st.session_state.kb_active = False
            st.session_state.uploaded_names = []
            st.rerun()
    else:
        st.markdown("**Status:** 🔴 Web Mode")

    st.divider()
    st.caption("Upload documents to enable knowledge-based answers")

# ────────────────────────────────────────────────────────────────
# 💬 Chat UI
# ────────────────────────────────────────────────────────────────

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f"<div class='chat-user'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-answer'>{message['content']}</div>", unsafe_allow_html=True)

# Input
user_query = st.chat_input("Ask anything...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(f"<div class='chat-user'>{user_query}</div>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                # 🔥 FIX: Ensure graph always initialized
                if st.session_state.graph is None:
                    st.session_state.graph = build_graph(vectorstore=None)

                result = st.session_state.graph.invoke({"query": user_query})

                answer = result.get("final_answer", "No response generated.")
                summary = result.get("summary", "")

                # Source Badge
                if result.get("used_rag"):
                    st.markdown("📚 *Knowledge Base*")
                else:
                    st.markdown("🌐 *Web Search*")

                st.markdown("---")

                st.markdown("<div class='section-title'>Answer</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-answer'>{answer}</div>", unsafe_allow_html=True)

                with st.expander("🧠 Summary"):
                    st.markdown(summary)

                with st.expander("📚 Sources"):
                    if result.get("used_rag"):
                        st.write("From uploaded documents")
                    else:
                        for doc in result.get("documents", [])[:3]:
                            st.write(doc["url"])

            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })