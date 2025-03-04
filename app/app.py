import streamlit as st
from streamlit_option_menu import option_menu

# 오프라인 환경에서 사용 가능한 session_manager 모듈
from app.utils.session_manager import initialize_session_state

# (선택) 기존 네비게이션 바 컴포넌트 (필요시 사용)
from app.components.navbar import render_navbar

# 각 페이지 컴포넌트 로딩
from app.pages.home_page import show_home
from app.pages.upload_page import render_upload_page
from app.pages.semantic_search_demo import render_query_page
from app.pages.llm_query_demo import render_llm_query_page

def main():
    # 1) 세션 스테이트 초기화
    initialize_session_state()
    
    # 2) 기본 UI 구성
    st.set_page_config(page_title="Demo App", layout="wide")

    # (선택) 기존 네비게이션 바 사용 가능
    # render_navbar()

    # 3) 새로운 멋진 네비게이션 바 (옵션 메뉴)
    selected = option_menu(
        menu_title=None,  # 메뉴 상단 타이틀 (None이면 숨김)
        options=["홈", "파일 업로드", "의미검색 데모", "LLM 질의응답 데모"],
        icons=["house", "cloud-upload", "search", "question"],  # Bootstrap 아이콘명
        menu_icon="cast",  # 전체 메뉴 아이콘 (왼쪽 상단 아이콘)
        default_index=0,  # 기본 선택 메뉴
        orientation="horizontal",  # 수평(horizontal) / 수직(vertical)
        styles={
            "container": {
                "padding": "0!important", 
                "background-color": "#fafafa",  # 전체 컨테이너 배경색
            },
            "icon": {
                "color": "#4CAF50",  # 아이콘 색상
                "font-size": "18px"
            }, 
            "nav-link": {
                "font-size": "16px",
                "font-weight": "bold",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "#eee",  # 마우스 오버 시 배경색
            },
            "nav-link-selected": {
                "background-color": "#4CAF50",  # 현재 페이지 선택 시 색상
                "color": "white"
            },
        }
    )

    # 4) 페이지 라우팅
    if selected == "홈":
        show_home()
    elif selected == "파일 업로드":
        render_upload_page()
    elif selected == "의미검색 데모":
        render_query_page()
    elif selected == "LLM 질의응답 데모":
        render_llm_query_page()

    # 5) 기타 필요한 로직...
    #    예: 오프라인 환경에서 사용할 로컬 번역 모델 초기화, 문서 처리 등

if __name__ == "__main__":
    main()
