import json
import os

def load_tech_regulations():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "..", "data", "tech_regulations.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 최상위가 딕셔너리라면 "documents" 키로 리스트를 반환합니다.
        documents = data.get("documents", [])
        return documents
    except Exception as e:
        print(f"[ERROR] 법령 데이터 로드 실패: {e}")
        return []
