import streamlit as st
import httpx
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="MindFlow", page_icon="🧠", layout="wide")
st.title("🧠 MindFlow — AI Second Brain")
st.caption("Ingest anything. Search everything. Ask your knowledge base.")

tab1, tab2, tab3 = st.tabs(["📥 Ingest", "🔍 Search", "💬 Ask"])

# ── TAB 1: INGEST ──────────────────────────────────────────────
with tab1:
    st.header("Add to your knowledge base")
    source_type = st.selectbox("Source type", ["manual", "url", "pdf"])
    title = st.text_input("Title (optional)")

    content = None
    file = None
    source_url = None

    if source_type == "manual":
        content = st.text_area("Paste your content here", height=200)

    elif source_type == "url":
        source_url = st.text_input("URL to scrape")

    elif source_type == "pdf":
        file = st.file_uploader("Upload a PDF", type=["pdf"])

    if st.button("Ingest"):
        with st.spinner("Ingesting..."):
            try:
                if source_type == "pdf" and file:
                    response = httpx.post(
                        f"{API_URL}/ingest",
                        data={"source_type": "pdf", "title": title or ""},
                        files={"file": (file.name, file.read(), "application/pdf")},
                        timeout=30,
                    )
                else:
                    data = {
                        "source_type": source_type,
                        "title": title or "",
                        "content": content or "",
                        "source_url": source_url or "",
                    }
                    response = httpx.post(f"{API_URL}/ingest", data=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Ingested successfully — ID: {result.get('id')}")
                    st.caption("Embeddings are being generated in the background.")
                else:
                    st.error(f"Failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# ── TAB 2: SEARCH ──────────────────────────────────────────────
with tab2:
    st.header("Semantic search")
    query = st.text_input("Search your knowledge base")
    limit = st.slider("Number of results", 1, 10, 5)

    if st.button("Search"):
        with st.spinner("Searching..."):
            try:
                response = httpx.get(
                    f"{API_URL}/search",
                    params={"q": query, "limit": limit},
                    timeout=15,
                )
                if response.status_code == 200:
                    results = response.json()
                    if not results:
                        st.info("No results found.")
                    for i, chunk in enumerate(results, 1):
                        with st.expander(f"Result {i} — {chunk.get('item_title', 'Untitled')} ({chunk.get('source_type')})"):
                            st.write(chunk.get("chunk_content"))
                else:
                    st.error(f"Search failed: {response.status_code}")
            except Exception as e:
                st.error(f"Request failed: {e}")

# ── TAB 3: ASK ─────────────────────────────────────────────────
with tab3:
    st.header("Ask your knowledge base")
    question = st.text_input("What do you want to know?")

    if st.button("Ask"):
        with st.spinner("Thinking..."):
            try:
                response = httpx.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=30,
                )
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer returned.")
                    st.markdown("### Answer")
                    st.write(answer)
                else:
                    st.error(f"Failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Request failed: {e}")