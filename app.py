import streamlit as st
from rag import retrieve, generate_answer
from logger import log_event

st.set_page_config(page_title="Agentic RAG – SANOVIO", layout="wide")

st.title("🧠 Agentic RAG Chatbot")
st.write("Ask questions about the German product catalog (answers in English).")

query = st.text_input("Your question")

if st.button("Ask") and query:
    retrieved, q_type = retrieve(query)
    log_event("query", {"query": query, "type": q_type})

    answer = generate_answer(query, retrieved)

    st.subheader("Answer")
    st.write(answer)

    with st.expander("Retrieved Sources"):
        for c in retrieved:
            st.markdown(f"**Page {c['page']}**")
            st.write(c["text"][:500] + "...")
