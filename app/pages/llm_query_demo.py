import streamlit as st
import time
import app.utils.query_utils as query_utils

def render_llm_query_page():
    st.header("LLM 질의응답 데모")

    # -----------------------------
    # (1) 세션 스테이트 초기화
    # -----------------------------
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "search_active" not in st.session_state:
        st.session_state["search_active"] = False
    if "latest_answer" not in st.session_state:
        st.session_state["latest_answer"] = ""
    if "embedding_model" not in st.session_state:
        st.session_state["embedding_model"] = "snowflake-arctic-embed2"
    if "clear_pending" not in st.session_state:
        st.session_state["clear_pending"] = False

    # 임베딩 모델 선택 UI
    embedding_model = st.selectbox(
        "임베딩 모델을 선택하세요:",
        options=["snowflake-arctic-embed2", "mxbai-embed-large"],
        index=0
    )
    st.session_state["embedding_model"] = embedding_model

    # -----------------------------
    # (2) 대화 내역 표시 영역 (History Box)
    # -----------------------------
    history_container = st.container()
    with history_container:
        st.subheader("대화 내역")
        if st.session_state["chat_history"]:
            history_html = "<div style='height:300px; overflow-y:auto; border:1px solid #ddd; padding:10px;'>"
            for msg in st.session_state["chat_history"]:
                role = msg["role"]
                content = msg["content"]
                if role == "user":
                    history_html += f"<p><strong>사용자:</strong> {content}</p>"
                else:
                    history_html += f"<p><strong>어시스턴트:</strong> {content}</p>"
            history_html += "</div>"
            st.markdown(history_html, unsafe_allow_html=True)
        else:
            st.info("대화 내역이 없습니다.")

    # -----------------------------
    # (3) 사용자 입력 영역 및 컨트롤
    # -----------------------------
    if "search_active" not in st.session_state:
        st.session_state["search_active"] = True

    user_input = st.text_input("질문을 입력하세요:", key="user_input")
    col1, col2 = st.columns(2)
    with col1:
        search_active = st.checkbox(
            "Semantic Search 활성화", 
            value=st.session_state["search_active"],
            key="semantic_search_checkbox"
        )
        st.session_state["search_active"] = search_active
        if search_active:
            st.markdown("<span style='color:blue;'>Semantic Search 활성화됨 (RAG)</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:gray;'>Semantic Search 비활성화됨 (일반 LLM)</span>", unsafe_allow_html=True)
    with col2:
        submit_clicked = st.button("질문 제출")

    # -----------------------------
    # (4) 쿼리 제출 처리
    # -----------------------------
    if submit_clicked:
        if not user_input:
            st.warning("질문을 입력하세요.")
        else:
            st.session_state["chat_history"].append(
                {"role": "user", "content": user_input}
            )
            if st.session_state["search_active"]:
                with st.spinner("RAG 처리 중..."):
                    result = query_utils.query_document(
                        user_input,
                        n_results=10,
                        response=True,
                        rerank=True,
                        embedding_model=st.session_state["embedding_model"]
                    )
                    response_text = result.get("generated_response", "")
                    time.sleep(1)
            else:
                with st.spinner("LLM 처리 중..."):
                    time.sleep(1)
                    response_text = query_utils.llm_response(
                        user_input,
                        st.session_state["chat_history"]
                    )
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": response_text}
            )
            st.session_state["latest_answer"] = response_text
            if "user_input" in st.session_state:
                del st.session_state["user_input"]

    # -----------------------------
    # (5) 최신 응답 영역 (Answer Box)
    # -----------------------------
    st.subheader("최근 응답")
    if st.session_state["latest_answer"]:
        st.markdown(
            f"<div style='border:1px solid #ddd; padding:10px;'>{st.session_state['latest_answer']}</div>", 
            unsafe_allow_html=True
        )
    else:
        st.info("최근 응답이 없습니다.")

    # -----------------------------
    # (6) 대화 초기화 버튼 (Clear Conversation)
    # -----------------------------
    # clear_pending 키에 따라 버튼 레이블 설정
    if st.button("대화 초기화"):
        st.session_state["chat_history"] = []
        st.session_state["latest_answer"] = ""
        if "user_input" in st.session_state:
            del st.session_state["user_input"]
        st.rerun()
