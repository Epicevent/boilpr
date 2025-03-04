import streamlit as st
import pandas as pd
import uuid
import os
import subprocess
import tempfile
import json
from app.utils.paser import parse_filename, text_to_dictionary  # 파일명 파싱 및 텍스트 파싱 함수

def convert_hwp_to_text(hwp_data: bytes) -> str:
    """
    LibreOffice를 이용하여 .hwp 파일의 바이트 데이터를 텍스트로 변환합니다.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        hwp_path = os.path.join(tmpdir, "upload.hwp")
        with open(hwp_path, "wb") as f:
            f.write(hwp_data)

        # LibreOffice 실행 환경 변수 설정
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = "/usr/lib/libreoffice/program:" + env.get("LD_LIBRARY_PATH", "")
        env["PATH"] = "/usr/lib/libreoffice/program:" + env.get("PATH", "")

        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "txt:Text",
            "--outdir", tmpdir,
            hwp_path
        ]
        try:
            subprocess.run(cmd, check=True, env=env)
        except subprocess.CalledProcessError as e:
            print("[오류] LibreOffice 변환 실패:", e)
            return ""

        txt_path = os.path.join(tmpdir, "upload.txt")
        if not os.path.exists(txt_path):
            return ""

        with open(txt_path, "r", encoding="utf-8", errors="replace") as txt_file:
            return txt_file.read()


def render_upload_page():
    """문서 업로드 및 표시 페이지"""
    st.header("📄 문서 업로드")

    # -----------------------------
    # 파일 업로드 영역
    # -----------------------------
    upload_col1, upload_col2 = st.columns([3, 1])
    
    with upload_col1:
        uploaded_files = st.file_uploader(
            "문서를 업로드하세요 (PDF/TXT/HWP)", 
            accept_multiple_files=True,
            type=["pdf", "txt", "hwp"],
            key=st.session_state["uploader_key"]
        )
    
    with upload_col2:
        st.write("")
        st.write("")
        st.markdown(" ", unsafe_allow_html=True)
        if st.button("📥 업로드"):
            if uploaded_files:
                new_files = False
                for uploaded_file in uploaded_files:
                    file_name = uploaded_file.name
                    file_type = uploaded_file.type
                    file_data = uploaded_file.getvalue()
                    
                    # 파일명 규칙 검사 및 메타데이터 추출
                    file_metadata = parse_filename(file_name)
                    
                    # 파일명이 규칙에 맞지 않더라도 메타데이터는 빈 상태로 만들어줌
                    if file_metadata is None:
                        file_metadata = {
                            "document_title": "",
                            "document_type": "",
                            "promulgation_number": "",
                            "enforcement_date": ""
                        }
                    
                    # HWP 파일인 경우
                    if file_name.lower().endswith(".hwp"):
                        converted_text = convert_hwp_to_text(file_data)
                        if converted_text.strip():
                            file_info = {
                                "id": str(uuid.uuid4()),
                                "name": file_name,
                                "size": len(converted_text.encode("utf-8")),
                                "type": "text/plain (HWP 변환됨)",
                                "data": converted_text.encode("utf-8")
                            }
                        else:
                            st.warning(f"{file_name} 파일을 텍스트로 변환하는 데 실패했습니다. 파일이 손상되었거나 호환되지 않을 수 있습니다.")
                            continue
                    else:
                        # PDF 또는 TXT 파일인 경우
                        file_info = {
                            "id": str(uuid.uuid4()),
                            "name": file_name,
                            "size": len(file_data),
                            "type": file_type,
                            "data": file_data
                        }
                    
                    # 업로드된 텍스트를 파싱하여 문서 구조 생성 (파싱 결과를 "structure"에 저장)
                    document = text_to_dictionary(
                        file_info["data"].decode("utf-8", errors="replace"),
                        file_info["id"],
                        file_metadata
                    )
                    file_info["structure"] = document
                    
                    # 중복 업로드 방지
                    if not any(doc["name"] == file_name for doc in st.session_state["uploaded_documents"]):
                        st.session_state["uploaded_documents"].append(file_info)
                        new_files = True

                if new_files:
                    st.success("문서가 성공적으로 업로드되었습니다!")
                else:
                    st.info("새로운 문서가 업로드되지 않았습니다.")
            else:
                st.warning("선택된 파일이 없습니다.")
            
            # 업로더 키 초기화
            st.session_state["uploader_key"] = str(uuid.uuid4())
            st.rerun()

    # -----------------------------
    # 업로드된 문서 표시 영역
    # -----------------------------
    if st.session_state["uploaded_documents"]:
        st.subheader("🗂️ 업로드된 문서")
        
        # 검색 기능
        search_query = st.text_input("🔍 문서 검색:")
        if search_query:
            filtered_docs = [
                doc for doc in st.session_state["uploaded_documents"]
                if search_query.lower() in doc["name"].lower()
            ]
        else:
            filtered_docs = st.session_state["uploaded_documents"]
        
        if filtered_docs:
            # 문서 목록을 표로 표시
            doc_df = pd.DataFrame([{
                "문서명": doc["name"],
                "크기 (KB)": f"{doc['size'] / 1024:.2f}",
                "파일 유형": doc["type"]
            } for doc in filtered_docs])
            st.table(doc_df)
            
            # 삭제할 문서 선택
            selected_docs_to_delete = st.multiselect(
                "삭제할 문서를 선택하세요:",
                [doc["name"] for doc in filtered_docs]
            )
            
            if st.button("🗑️ 선택 문서 삭제"):
                st.session_state["uploaded_documents"] = [
                    doc for doc in st.session_state["uploaded_documents"]
                    if doc["name"] not in selected_docs_to_delete
                ]
                st.success("선택한 문서가 삭제되었습니다.")
                st.rerun()
        else:
            st.info("검색 결과에 해당하는 문서가 없습니다.")
    else:
        st.info("업로드된 문서가 없습니다.")
