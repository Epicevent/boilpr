import streamlit as st
import pandas as pd


def render_query_page():
    st.header("🔍 의미검색 데모")

    # 임베딩 모델 선택 UI (기본값: snowflake-arctic-embed2)
    embedding_model = st.selectbox(
        "임베딩 모델을 선택하세요:",
        options=["snowflake-arctic-embed2", "mxbai-embed-large"],
        index=0
    )

    if "prev_embedding_model" not in st.session_state:
        st.session_state["prev_embedding_model"] = embedding_model
    elif st.session_state["prev_embedding_model"] != embedding_model:
        st.session_state["prev_embedding_model"] = embedding_model
        st.rerun()

    st.session_state["embedding_model"] = embedding_model

    # 검색 범위 선택 메뉴
    search_scope = st.selectbox(
        "검색 범위를 선택하세요:",
        options=["전체 문서", "내 문서", "기술기획 관령 법령", "기타"]
    )
    st.write("선택한 검색 범위:", search_scope)
    
    # 기본은 '기술기획 관령 법령'이지만, 나머지 범위에서는 파일 검색 데모가 구현되지 않았음을 안내
    if search_scope in ["전체 문서", "내 문서", "기타"]:
        st.info("사용자가 올린 파일 검색 데모는 아직 구현되지 않았습니다. 구현 후 이 메시지는 사라집니다.")

    # 폼(form) 구성
    with st.form(key="search_form"):
        st.subheader("🔍 Query Input")
        query = st.text_input("검색어를 입력하세요:")
        submit_button = st.form_submit_button(label="🔍 검색 실행")

    if submit_button and query:
        import app.utils.query_utils as query_utils
        with st.spinner("검색어 처리 중..."):
            result = query_utils.query_document(
                query,
                n_results=1,
                response=False,
                rerank=False,
                embedding_model=st.session_state["embedding_model"]
            )
            st.session_state["search_result"] = result
        st.text(result["retrieved_document"])

    # 선택한 검색 범위에 따른 문서 목록 표시
    st.subheader("📄 문서 목록")
    docs = []
    if search_scope == "내 문서":
        docs = st.session_state.get("uploaded_documents", [])
    elif search_scope == "기술기획 관령 법령":
        docs = st.session_state.get("tech_regulations", [])
    elif search_scope == "전체 문서":
        docs = st.session_state.get("uploaded_documents", []) + st.session_state.get("tech_regulations", [])
    elif search_scope == "기타":
        docs = []  # 기타 범위

    if docs:
        doc_df = pd.DataFrame([
            {"문서 제목": doc.get("document_title", doc.get("name", "No Title"))}
            for doc in docs
        ])
        st.table(doc_df)
    else:
        st.info("선택한 범위에 문서가 없습니다. 문서를 업로드하거나 데이터가 추가되면 표시됩니다.")
