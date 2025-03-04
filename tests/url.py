import requests
import urllib.parse

def fetch_regulation(regulation_title: str, promulgation_number: str, enforcement_date: str, oc: str = "test@example.com", response_type: str = "JSON") -> str:
    """
    정부 법령(행정규칙) URL 패턴을 이용해 문서를 가져오는 함수.
    
    매개변수:
      regulation_title: 규칙제목 (예: "국방전략발전업무훈령")
      promulgation_number: 공포번호 (예: "3007")
      enforcement_date: 시행일자 (예: "20250110")
      oc: 요청에 사용할 OC 값 (기본값은 테스트용 이메일)
      response_type: 응답 형식 (JSON, XML, HTML 중 선택; 여기서는 URL 구성에만 사용)
      
    반환:
      요청에 대한 응답 텍스트 (또는 오류 메시지)
    """
    # 규칙제목은 URL 인코딩 처리 (예: "국방전략발전업무훈령" → %EA%B5%AD%EB%B0%A9%EC%A0%84%EB%A0%A5%EB%B0%9C%EC%A0%84%EC%97%85%EB%AC%B4%ED%9B%88%EB%A0%B9)
    encoded_title = urllib.parse.quote(regulation_title)
    
    # URL 패턴에 맞게 경로 구성
    # 예시: https://www.law.go.kr/행정규칙/국방전략발전업무훈령/
    base_url = "https://www.law.go.kr/%ED%96%89%EC%A0%95%EA%B7%9C%EC%B9%99/%EA%B5%AD%EB%B0%A9%EC%A0%84%EB%A0%A5%EB%B0%9C%EC%A0%84%EC%97%85%EB%AC%B4%ED%9B%88%EB%A0%B9"
    path = f"/행정규칙/{encoded_title}"
    full_url = base_url #+ path
    
    # 실제 API 호출 (여기서는 단순 GET 요청)
    try:
        response = requests.get(full_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching regulation: {e}"

# 예시 실행:
if __name__ == "__main__":
    # 사용자가 정확한 규칙 제목과 공포번호, 시행일자를 입력한다고 가정
    regulation_title = "국방전략발전업무훈령"  # 정확한 규칙 제목
    promulgation_number = "3007"              # 예: 공포번호
    enforcement_date = "20250110"             # 예: 시행일자
    
    result = fetch_regulation(regulation_title, promulgation_number, enforcement_date)
    print("Fetched Regulation Data:")
    print(result)
