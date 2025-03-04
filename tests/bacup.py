import streamlit as st
import uuid
import time
import pandas as pd

# -----------------------------
# (예시) Ground Truth JSON (데모용)
# -----------------------------
GROUND_TRUTH = {
  "queries": [
    {
      "query": "양산 총사업비 협의 언제 이루어지나요?",
      "content": [
        {
            "chunk_id": "1.22.3",
            "chunk_type": "paragraph",
            "metadata_text": "「방위사업관리규정」 22조3항",
            "content": "통합사업관리팀장은 제2항에 따른 양산 총사업비 심층검토 결과를 근거로 기획재정부장관에게 양산 예산 및 총사업비 협의 등을 요구할 수 있다."
        },
        {
            "chunk_id": "1.22",
            "chunk_type": "article",
            "metadata_text": "「방위사업관리규정」 22조의2 (양산 총사업비 심층검토)",
            "content": "통합사업관리팀장은 「국방사업 총사업비 관리지침」에 따라 연구개발 사업 타당성조사를 통해 추정한 양산 총사업비의 변동여부 등을 세부적으로 검토하기 위해 잠정전투용적합 또는 개발 시험평가 결과 기준총족 판정을 받은 이후에 방위사업정책국장에게 양산 총사업비 심층검토 요청을 의뢰할 수 있다.  방위사업정책국장은 제1항에 따라 양산 총사업비 심층검토 요청을 의뢰받은 경우 한국국방연구원 등 전문연 구기관에 분석을 의뢰하여야 하고, 그 결과를 통합사업관리팀장에게 통보한다.  통합사업관리팀장은 제2항에 따른 양산 총사업비 심층검토 결과를 근거로 기획재정부장관에게 양산 예산 및 총사업비 협의 등을 요구할 수 있다."
        }
      ]
    },
    {
      "query": "예산편성자료 제출 시점은 언제인가요?",
      "content": [
        {
            "chunk_id": "1.23.2",
            "chunk_type": "paragraph",
            "metadata_text": "「방위사업관리규정」 23조2항",
            "content": "국과연은 국방중기계획과 국방부 예산편성지침을 근거로 국과연주관 무기체계 및 핵심기술 연구개발사업과 연구지원분야 등에 대한 예산편성자료를 작성하여 사업본부 및 국방기술보호국에 각각 제출한다."
        },
        {
            "chunk_id": "1.23.3",
            "chunk_type": "paragraph",
            "metadata_text": "「방위사업관리규정」 23조3항",
            "content": "기품원은 영 제71조제2항에 따라 함정 무기체계 연구개발의 품질보증과 형상관리 기술지원 등에 대한 예산편 성자료를 작성하여 사업본부에 제출한다."
        }
      ]
    },

  ]
}

# -----------------------------
# 간단한 검색 함수 (데모용)
# -----------------------------
def get_ground_truth_results(user_query: str):
    """
    user_query와 GROUND_TRUTH['queries'] 내 query가
    '완전히 동일'할 때만 해당 content를 반환하는 간단한 예시 함수.
    """
    matched_contents = []
    for item in GROUND_TRUTH["queries"]:
        if user_query.strip() == item["query"]:
            for c in item["content"]:
                # chunk_id, content 합쳐서 보기 좋게 문자열 구성
                matched_contents.append(
                    f"**Chunk {c['metadata_text']}**\n\n{c['content']}"
                )
    return matched_contents


# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(page_title="📄🔍 RAG System Prototype", layout="wide")
st.title("📄🔍 RAG System Prototype")

# -----------------------------
# Initialize Session State
# -----------------------------
if "uploaded_documents" not in st.session_state:
    st.session_state["uploaded_documents"] = []

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = str(uuid.uuid4())

if "query_results" not in st.session_state:
    st.session_state["query_results"] = []

# -----------------------------
# Sidebar: Settings
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    
    with st.expander("🔤 Translation & Embedding Methods", expanded=True):
        translate_methods = ["Easy", "Mbart50", "MarianMT", "T5", "Pegasus", "Google Translate"]
        embedding_methods = ["SBERT", "BERT", "FastText", "GPT-3", "Word2Vec"]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_translate = st.selectbox("Select Translation Method", translate_methods, index=0)
        with col2:
            selected_embedding = st.selectbox("Select Embedding Method", embedding_methods, index=0)
    
    with st.expander("📈 Query Parameters", expanded=True):
        top_k = st.slider("Number of Results (Top K)", min_value=1, max_value=10, value=5)
    
    if st.button("🧹 Clear All Data"):
        st.session_state.clear()
        st.success("Session state cleared!")
        st.rerun()

# -----------------------------
# Document Upload Section
# -----------------------------
st.header("📄 Document Upload")

upload_col1, upload_col2 = st.columns([3, 1])

with upload_col1:
    uploaded_files = st.file_uploader(
        "Upload your documents (PDF/TXT)",
        accept_multiple_files=True,
        key=st.session_state["uploader_key"]
    )

with upload_col2:
    st.write("")
    st.write("")
    st.markdown(" ", unsafe_allow_html=True)
    st.markdown(" ", unsafe_allow_html=True)
    if st.button("📥 Upload"):
        if uploaded_files:
            new_files = False
            for uploaded_file in uploaded_files:
                file_info = {
                    "id": str(uuid.uuid4()),
                    "name": uploaded_file.name,
                    "size": len(uploaded_file.getvalue()),
                    "type": uploaded_file.type,
                    "data": uploaded_file.getvalue()
                }
                # Prevent duplicates based on file name
                if not any(doc["name"] == uploaded_file.name for doc in st.session_state["uploaded_documents"]):
                    st.session_state["uploaded_documents"].append(file_info)
                    new_files = True
            if new_files:
                st.success("Documents uploaded successfully!")
            else:
                st.info("No new documents to upload.")
        else:
            st.warning("No files selected.")
        
        # Reset the uploader
        st.session_state["uploader_key"] = str(uuid.uuid4())
        st.rerun()

# -----------------------------
# Display Uploaded Documents
# -----------------------------
if st.session_state["uploaded_documents"]:
    st.subheader("🗂️ Uploaded Documents")
    
    search_query = st.text_input("🔍 Search Documents:")
    if search_query:
        filtered_docs = [doc for doc in st.session_state["uploaded_documents"] 
                         if search_query.lower() in doc["name"].lower()]
    else:
        filtered_docs = st.session_state["uploaded_documents"]
    
    if filtered_docs:
        doc_df = pd.DataFrame([{
            "Name": doc["name"],
            "Size (KB)": f"{doc['size'] / 1024:.2f}",
            "Type": doc["type"]
        } for doc in filtered_docs])
        st.table(doc_df)
        
        selected_docs_to_delete = st.multiselect("Select documents to delete:", [doc["name"] for doc in filtered_docs])
        
        if st.button("🗑️ Delete Selected Documents"):
            st.session_state["uploaded_documents"] = [
                doc for doc in st.session_state["uploaded_documents"]
                if doc["name"] not in selected_docs_to_delete
            ]
            st.success("Selected documents deleted!")
            st.rerun()
    else:
        st.info("No documents match your search.")

# -----------------------------
# Query Input Section
# -----------------------------
st.header("🔍 Query Input")

query_col1, query_col2 = st.columns([3, 1])

with query_col1:
    query = st.text_input("Enter your query:")

with query_col2:
    st.write("")
    st.markdown(" ", unsafe_allow_html=True)
    submit_query = st.button("🔍 Submit Query")

if submit_query and query:
    with st.spinner("Processing your query..."):
        time.sleep(2)  # 가상의 처리 지연
        
        # (1) Ground Truth 기반 데모 검색
        ground_truth_matches = get_ground_truth_results(query)
        
        # (2) 결과 구성
        if ground_truth_matches:
            # ground_truth_matches가 있는 경우 → 해당 결과를 세션에 저장
            # 여기서는 top_k 제한 (슬라이더)도 걸어본다
            sliced_results = ground_truth_matches[:top_k]
            st.session_state["query_results"] = sliced_results
        else:
            # Ground Truth에 없을 때는 'No match found'라고만 표시
            st.session_state["query_results"] = ["No match found in Ground Truth."]
    
    st.success("Query processed!")
    
# -----------------------------
# Display Query Results
# -----------------------------
if st.session_state["query_results"]:
    st.subheader("📄 Query Results")
    for i, result in enumerate(st.session_state["query_results"]):
        with st.expander(f"Result {i+1}"):
            st.markdown(result)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("👨‍💻 Built with [Streamlit](https://streamlit.io/) for RAG System Prototyping.")