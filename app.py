import warnings
warnings.filterwarnings("ignore")
import streamlit as st

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from database import create_vectorstore
from prompts import SUMMARY_PROMPT, CONTRIBUTION_PROMPT, QA_PROMPT
from llm import get_llm


st.set_page_config(page_title="ResearchIQ", layout="wide")


st.markdown("""
<style>
    .block-container { padding-top: 3rem; padding-bottom: 1rem; }
    .stDeployButton { display: none; }
    h1 { margin: 0 0 0.25rem 0 !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)


def sample_context_docs(docs, frac=0.2):
    n = len(docs)
    if n == 0:
        return []
    chunk = max(1, int(n * frac))
    front_idx = set(range(0, min(chunk, n)))
    mid_start = max(0, (n // 2) - (chunk // 2))
    mid_idx = set(range(mid_start, min(mid_start + chunk, n)))
    end_idx = set(range(max(0, n - chunk), n))
    selected = sorted(front_idx | mid_idx | end_idx)
    return [docs[i] for i in selected]


DEFAULT_STATE = {
    "summary": "", "contributions": "", "chat_history": [],
    "page": "Summary", "docs": [],
    "retriever": None, "uploaded_file_id": None,
}

if "chat_history" not in st.session_state:
    st.session_state.update(DEFAULT_STATE)


st.title("ResearchIQ")
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed", key="pdf_uploader")

st.divider()


if uploaded_file is not None:
    current_id = f"{uploaded_file.name}-{uploaded_file.size}"
    if current_id != st.session_state.get("uploaded_file_id"):
        st.session_state.update(DEFAULT_STATE)
        st.session_state["uploaded_file_id"] = current_id

        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Processing PDF..."):
            loader = PyMuPDFLoader("temp.pdf")
            docs = loader.load()
            chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)

            if not chunks:
                st.session_state["uploaded_file_id"] = None
                st.error(
                    "Couldn't extract any text from this PDF. It may be a scanned "
                    "or image-only document (no selectable text layer). Try a "
                    "different PDF, or one that's been OCR-processed."
                )
                st.stop()

            vectorstore = create_vectorstore(chunks, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
            st.session_state.update({
                "docs": docs,
                "retriever": vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 8})
            })
            st.rerun()


if st.session_state.docs:

    nav1, nav2, nav3 = st.columns(3)
    if nav1.button("Summary", use_container_width=True): st.session_state.page = "Summary"
    if nav2.button("Contributions", use_container_width=True): st.session_state.page = "Contributions"
    if nav3.button("Chat", use_container_width=True): st.session_state.page = "Chat"
    st.write("")


    if st.session_state.page == "Summary":
        st.subheader("Summary")
        if not st.session_state.summary:
            if st.button("Generate Summary"):
                with st.spinner("Generating Summary..."):
                    context = "\n".join([d.page_content for d in sample_context_docs(st.session_state.docs)])
                    prompt = SUMMARY_PROMPT.format(context=context, page_count=len(st.session_state.docs))
                    st.session_state.summary = get_llm().invoke(prompt).content
                st.rerun()
        else:
            st.markdown(st.session_state.summary)

    elif st.session_state.page == "Contributions":
        st.subheader("Contributions")
        if not st.session_state.contributions:
            if st.button("Generate Contributions"):
                with st.spinner("Generating Contributions..."):
                    context = "\n".join([d.page_content for d in sample_context_docs(st.session_state.docs)])
                    st.session_state.contributions = get_llm().invoke(CONTRIBUTION_PROMPT.format(context=context)).content
                st.rerun()
        else:
            st.markdown(st.session_state.contributions)

    elif st.session_state.page == "Chat":
        st.subheader("Document Query Engine")

        if st.session_state.chat_history:
            chat_area = st.container(height=450)
            for chat in st.session_state.chat_history:
                chat_area.chat_message("user").write(chat["user"])
                chat_area.chat_message("assistant").write(chat["ai"])
        else:
            st.info("Ask question (e.g., what is machine learning?)")

        if question := st.chat_input("Ask anything..."):
            retrieved_docs = st.session_state.retriever.invoke(question)
            context = "\n\n".join([f"[Page {d.metadata.get('page',0)+1}]\n{d.page_content}" for d in retrieved_docs])
            response = get_llm().invoke(QA_PROMPT.format(context=context, question=question))
            st.session_state.chat_history.append({"user": question, "ai": response.content})
            st.rerun()