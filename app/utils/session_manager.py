# app/utils/session_manager.py

import uuid
import streamlit as st
from app.utils.load_regulations import load_tech_regulations

def initialize_session_state():
    """오프라인 환경에서 사용할 세션 스테이트를 모두 초기화."""
    if "uploaded_documents" not in st.session_state:
        st.session_state["uploaded_documents"] = []

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = str(uuid.uuid4())

    if "query_results" not in st.session_state:
        st.session_state["query_results"] = []

    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = None
    # 그 외 필요한 세션 변수들을 추가
    # 예: 로컬 모델, 사전, 환경설정 값 등
    if "local_model" not in st.session_state:
        st.session_state["local_model"] = None
    if "tech_regulations" not in st.session_state:
        # 기술기획 관령 법령 데이터를 로드합니다.
        st.session_state["tech_regulations"] = load_tech_regulations()
