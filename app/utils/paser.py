import os
import re
import json
import sys
import subprocess
import tempfile
def save_to_json_file(data, file_name="parsed_document.json"):
    """
    Saves the given data to a JSON file.
    
    Args:
        data (dict): The parsed document structure to save.
        file_name (str): The name of the JSON file to save the data.
    """
    try:
        with open(file_name, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"[INFO] Data successfully saved to {file_name}")
    except Exception as e:
        print(f"[ERROR] Failed to save JSON file: {e}")
###########################################
# 1) 파일명에서 메타데이터 추출
###########################################
def parse_filename(file_name):
    """
    예) 방위사업관리규정(방위사업청훈령)(제864호)(20240711).hwp
    에서 document_title, document_type, promulgation_number, enforcement_date 추출
    """
    base_name = os.path.splitext(file_name)[0]
    pattern = re.compile(r"^(.*?)\((.*?)\)\((.*?)\)\((\d{8})\)$")
    match = pattern.match(base_name)
    if match:
        return {
            "document_title": match.group(1).strip(),
            "document_type": match.group(2).strip(),
            "promulgation_number": match.group(3).strip(),
            "enforcement_date": match.group(4).strip()
        }
    else:
        print(f"Filename '{file_name}' does not match the expected pattern.")
        return {
            "document_title": base_name,
            "document_type": "",
            "promulgation_number": "",
            "enforcement_date": ""
        }

###########################################
# 2) 로컬 HWP 파일 → bytes 로 읽기
###########################################
def get_hwp_bytes(hwp_path: str) -> bytes:
    """
    Reads the .hwp file at 'hwp_path' and returns its contents as a bytes object.
    """
    with open(hwp_path, "rb") as f:
        file_data = f.read()
    return file_data

###########################################
# 3) HWP bytes → 텍스트 (LibreOffice)
###########################################
def convert_hwp_to_text(hwp_data: bytes) -> str:
    """
    Converts .hwp bytes to text using LibreOffice with enforced environment variables.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        hwp_path = os.path.join(tmpdir, "upload.hwp")
        with open(hwp_path, "wb") as f:
            f.write(hwp_data)

        # Force system paths for LibreOffice
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
            print("[ERROR] LibreOffice conversion failed:", e)
            return ""

        txt_path = os.path.join(tmpdir, "upload.txt")
        if not os.path.exists(txt_path):
            return ""

        with open(txt_path, "r", encoding="utf-8", errors="replace") as txt_file:
            return txt_file.read()
###########################################
# 4) {전문} 기준으로 조문목록 / 본문 분리
###########################################
def split_jomun_list_and_main_text(full_text, marker="{전문}"):
    lines = full_text.split("\n")
    jomun_list_lines = []
    main_text_lines = []
    found_marker = False

    for line in lines:
        if not found_marker:
            if line.strip() == marker:
                found_marker = True
            else:
                jomun_list_lines.append(line)
        else:
            main_text_lines.append(line)
    
    # If the marker was not found, treat all text as main_text
    if not found_marker:
        main_text_lines = lines
        jomun_list_lines = []

    jomun_list_text = "\n".join(jomun_list_lines)
    main_text = "\n".join(main_text_lines)
    return jomun_list_text, main_text

###########################################
# 5) 유효 라인(“제n조”, “1.” 등)만 추출
###########################################
VALID_LINE_PATTERN = re.compile(
    r"^"                             
    r"(?:"
    # "제 n (장|절|조(의\d+)?)" -> 예: 제1장, 제2절, 제3조, 제3조의2
    r"제\s*\d+(?:장|절|조(?:의\d+)?)"
    r"|"
    # 숫자열거자 "1.", "2."
    r"\d+\.\s*"
    r"|"
    # 한글열거자: "가.", "나.", ...
    r"[가나다라마바사아자차카타파하]\.\s*"
    r"|"
    # 괄호열거자: ① ~ ㉟
    r"[①-㉟]"
    r")"
)

def is_valid_line(line: str) -> bool:
    return bool(VALID_LINE_PATTERN.match(line.strip()))

def extract_valid_lines(text: str):
    kept = []
    for ln in text.split("\n"):
        ln_str = ln.strip()
        if ln_str and is_valid_line(ln_str):
            kept.append(ln_str)
    return kept

###########################################
# 6) 조문목록: 기사 번호만 추출
###########################################
ARTICLE_LIST_PATTERN = re.compile(r"^제\s*(\d+조(?:의\d+)?)(?:\(([^)]*)\))?")

def extract_article_numbers_from_jomun(jomun_lines):
    article_numbers = set()
    for line in jomun_lines:
        match = ARTICLE_LIST_PATTERN.match(line)
        if match:
            article_numbers.add(match.group(1))  # "1조", "67조", "67조의2" 등
    return article_numbers

###########################################
# 7) 본문 파싱: "제n조(제목) 뒷부분..."
###########################################

# 1) 하드코딩된 열거자 리스트
LEVEL1_ENUMS = [
    "①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩",
    "⑪","⑫","⑬","⑭","⑮","⑯","⑰","⑱","⑲","⑳",
    "㉑","㉒","㉓","㉔","㉕","㉖","㉗","㉘","㉙","㉚",
    "㉛","㉜","㉝","㉞","㉟"
]

LEVEL3_ENUMS = [
    "가.", "나.", "다.", "라.", "마.", "바.", "사.", "아.", "자.", "차.",  "카.", "타.", "파.", "하."
]

# 2) 동적으로 정의된 열거자 패턴
LEVEL2_PATTERN = re.compile(r"^\d+\.\s*")    # 예: 1., 2., 3., ..., 35.
LEVEL4_PATTERN = re.compile(r"^\d+\)\s*")    # 예: 1), 2), 3), ..., 35)

SECTION_REGEX = re.compile(r"^제\s*(\d+장|\d+절|\d+조(?:의\d+)?)(?:\s+([^\(①]*)\s*)?(?:\((.*?)\))?\s*(.*)$")




def parse_text_to_structure(lines, doc_id, title):
    """
    Parses text into a hierarchical structure of 장 → 절 → 조 → 항 → 호 → 목 → 하위목.
    """
    # Initialize the document structure
    if not title:
        title = f"문서 {doc_id}"
    if not doc_id:
        doc_id = 1

    document = {
        "document_id": str(doc_id),
        "document_title": title,
         "document_type": "",
        "promulgation_number": "",
        "enforcement_date": "",
        "chapters": []  # Top-level container for 장
    }

    # Current context for hierarchy
    current_chapter = None
    current_section = None
    current_article = None
    current_paragraph = None
    current_item = None
    current_subitem = None
    current_subsubitem = None
    
    # Add a default chapter for direct articles under the document
    current_chapter = {
        "chapter_number": "default",
        "chapter_title": "",
        "sections": []
    }



    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = SECTION_REGEX.match(line)
        if match:
            level = match.group(1)  # 장, 절, 조
            title = match.group(2) or ""  # 제목 (괄호 밖 제목)
            bracket_title = match.group(3) or ""  # 제목 (괄호 안 제목)
            text = match.group(4) or ""  # 본문
            
            # Combine title from both sources (if applicable)
            if level.endswith("조"):
                full_title = bracket_title
            else:
                full_title = title

            if "장" in level:
                # Close the current article
                if current_article:
                    current_section["articles"].append(current_article)
                    current_article = None

                # Close the current section
                if current_section:
                    current_chapter["sections"].append(current_section)
                    current_section = None

                # Close the current chapter
                if current_chapter and current_chapter["sections"]:
                    document["chapters"].append(current_chapter)

                # Start a new chapter
                current_chapter = {
                    "chapter_number": level,
                    "chapter_title": full_title,
                    "sections": []
                }

                # Add a default section for direct articles under the chapter
                current_section = {
                    "section_number": "default",
                    "section_title": "",
                    "articles": []
                }

            elif "절" in level:

                # Close the current article
                if current_article:
                    current_section["articles"].append(current_article)
                    current_article = None

                # Close the current section
                if current_section and current_section["articles"]:
                    current_chapter["sections"].append(current_section)

                # Start a new section
                current_section = {
                    "section_number": level,
                    "section_title": full_title,
                    "articles": []
                }

            elif "조" in level:
                if current_section is None:
                    current_section = {
                        "section_number": "default",
                        "section_title": "",
                        "articles": []
                    }   
                # Close the current article
                if current_article:
                    current_section["articles"].append(current_article)

                # Start a new article

                current_article = {
                    "article_number": level,
                    "article_title": full_title,
                    "article_text": "",
                    "paragraphs": []
                }
                # Check if the text contains "①"
                if "①" in text:
                    # Split the text into article text and paragraphs
                    parts = text.split("①", 1)
                    

                    # Create the first paragraph
                    current_paragraph = {
                        "paragraph_symbol": "①",
                        "paragraph_text": parts[1].strip(),  # Text after "①"
                        "items": []
                    }
                    current_article["paragraphs"].append(current_paragraph)
                else:
                    # Add a default paragraph if no "①" exists
                    current_paragraph = {
                        "paragraph_symbol": "①",
                        "paragraph_text": text.strip(),
                        "items": []
                    }
                    current_article["paragraphs"].append(current_paragraph)
            continue


        # Handle Paragraph (항)
        if current_article and any(line.startswith(symbol) for symbol in LEVEL1_ENUMS):
            for symbol in LEVEL1_ENUMS:
                if line.startswith(symbol):
                    content = line[len(symbol):].strip()
                    current_paragraph = {
                        "paragraph_symbol": symbol,
                        "paragraph_text": content,
                        "items": []
                    }
                    current_article["paragraphs"].append(current_paragraph)
                    current_item = None
                    current_subitem = None
                    current_subsubitem = None
                    break
            continue

        # Handle Item (호)
        match_level2 = LEVEL2_PATTERN.match(line)
        if match_level2 and current_paragraph:
            enumerator = match_level2.group(0).strip()
            content = line[match_level2.end():].strip()
            current_item = {
                "item_symbol": enumerator.rstrip('.'),
                "item_text": content,
                "subitems": []
            }
            current_paragraph["items"].append(current_item)
            current_subitem = None
            current_subsubitem = None
            continue

        # Handle Subitem (목)
        if current_item and any(line.startswith(symbol) for symbol in LEVEL3_ENUMS):
            for symbol in LEVEL3_ENUMS:
                if line.startswith(symbol):
                    content = line[len(symbol):].strip()
                    current_subitem = {
                        "subitem_symbol": symbol.rstrip('.'),
                        "subitem_text": content,
                        "subsubitems": []
                    }
                    current_item["subitems"].append(current_subitem)
                    current_subsubitem = None
                    break
            continue

        # Handle SubSubItem (하위목)
        match_level4 = LEVEL4_PATTERN.match(line)
        if match_level4 and current_subitem:
            enumerator = match_level4.group(0).strip()
            content = line[match_level4.end():].strip()
            current_subsubitem = {
                "subsubitem_symbol": enumerator.rstrip(')'),
                "subsubitem_text": content
            }
            current_subitem["subsubitems"].append(current_subsubitem)
            continue

        # General Text Continuation
        if current_article:
            if current_subsubitem:
                current_subsubitem["subsubitem_text"] += " " + line
            elif current_subitem:
                current_subitem["subitem_text"] += " " + line
            elif current_item:
                current_item["item_text"] += " " + line
            elif current_paragraph:
                current_paragraph["paragraph_text"] += " " + line
            else:
                current_article["article_text"] += " " + line

    # Close the remaining structures
    if current_article:
        if current_section:
            current_section["articles"].append(current_article)
        else:
            current_chapter["articles"].append(current_article)
    if current_section:
        current_chapter["sections"].append(current_section)
    if current_chapter:
        document["chapters"].append(current_chapter)

    return document


def extract_recognized_article_numbers(parsed_doc):
    """
    Recursively extracts all article numbers from the parsed document.
    Navigates through chapters → sections → articles.
    """
    recognized_nums = []

    for chapter in parsed_doc.get("chapters", []):
        # Articles directly under the chapter
        for article in chapter.get("articles", []):
            recognized_nums.append(article["article_number"])
        
        # Sections under the chapter
        for section in chapter.get("sections", []):
            for article in section.get("articles", []):
                recognized_nums.append(article["article_number"])

    return recognized_nums

###########################################
# 8) 조문목록 vs. 본문 파싱 결과 비교
###########################################
def compare_jomun_and_parsed(jomun_article_nums, parsed_document):
    """
    Compares the set of article numbers from the 조문목록
    to the parser's recognized articles in the parsed document.
    """
    # Extract recognized article numbers from the hierarchical structure
    recognized_nums = extract_recognized_article_numbers(parsed_document)

    # Convert to sets for comparison
    recognized_set = set(recognized_nums)
    missing = jomun_article_nums - recognized_set
    extra = recognized_set - jomun_article_nums

    return missing, extra


###########################################
# 9) 종합 테스트 함수 (단순 예시)
###########################################
def step3_test_parser(jomun_lines, main_lines, doc_id=1, doc_title="(제목미상)"):
    jomun_article_nums = extract_article_numbers_from_jomun(jomun_lines)
    
    parsed_doc = parse_text_to_structure(main_lines, doc_id, doc_title)
    
    missing, extra = compare_jomun_and_parsed(jomun_article_nums, parsed_doc)
    
    
    print("\n=== Comparison Results ===")
    print("조문목록:", jomun_article_nums)
    recognized_nums = extract_recognized_article_numbers(parsed_doc)
    print("본문에서 인식된 기사:", recognized_nums)
    if missing:
        print(f"[MISSING] {missing}")
    else:
        print("[OK] Missing 없음")
    
    if extra:
        print(f"[EXTRA] {extra}")
    else:
        print("[OK] Extra 없음")

###########################################
# 10) 사용 예시
###########################################
def convert_pdfs_to_json(folder_path, output_file):
    """
    Reads all PDFs in the given folder, parses them into structured JSON, 
    and writes the result to a JSON file.
    
    지정된 폴더의 모든 PDF 파일을 읽고, 파싱한 구조화 데이터를
    JSON 파일로 저장합니다.
    """
    documents = []
    for doc_id, file_name in enumerate(os.listdir(folder_path), start=1):
        if file_name.lower().endswith(".hwp"):
            hwp_path = os.path.join(folder_path, file_name)
            # 파일 이름에서 메타데이터 추출
            metadata = parse_filename(file_name)
            text = convert_hwp_to_text(get_hwp_bytes(hwp_path))
            jomun_text, main_text = split_jomun_list_and_main_text(text, marker="{전문}")
            text = extract_valid_lines(main_text)

            if text:
                print(f"Processing {file_name}...")
                structured_data = parse_text_to_structure(
                    text, 
                    doc_id, 
                    metadata["document_title"]
                )
                print(f"Extracted {len(structured_data['chapters'])} chapters.")
                # 메타데이터 추가
                structured_data["document_type"] = metadata["document_type"]
                structured_data["promulgation_number"] = metadata["promulgation_number"]
                structured_data["enforcement_date"] = metadata["enforcement_date"]
                documents.append(structured_data)

    print(f"Processed {len(documents)} PDF(s).")
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump({"documents": documents}, json_file, indent=4, ensure_ascii=False)

    print(f"Processed {len(documents)} PDF(s). JSON saved to {output_file}")
    save_to_json_file({"documents": documents}, output_file)

def text_to_dictionary(text, doc_id,metadata):
    """
    Converts the given text to a structured dictionary.
    """
    jomun_text, main_text = split_jomun_list_and_main_text(text, marker="{전문}")
    text = extract_valid_lines(main_text)
    title = metadata["document_title"]
    structured_data = parse_text_to_structure(text, doc_id, title)
    # 메타데이터 추가
    structured_data["document_type"] = metadata["document_type"]
    structured_data["promulgation_number"] = metadata["promulgation_number"]
    structured_data["enforcement_date"] = metadata["enforcement_date"]
    return structured_data
    

if __name__ == "__main__":
    """
    Main entry point. 
    Usage: Just run this script; it will look for PDF files in 'pdfs' folder 
    and produce 'output.json'.
    
    이 스크립트의 메인 실행부입니다.
    'pdfs' 폴더 내의 PDF 파일을 모두 찾아 파싱한 뒤, 'output.json'으로 저장합니다.
    """
    folder_path = "../hwps"         # 폴더 경로
    output_file = "../output.json"  # 결과를 저장할 JSON 파일명
    convert_pdfs_to_json(folder_path, output_file)