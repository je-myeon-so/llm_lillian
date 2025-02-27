import pdfplumber
import json
import re
import openai
from src.config import OPENAI_API_KEY

# OpenAI 클라이언트 생성
client = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o"

# PDF에서 텍스트 추출하는 함수
def extract_text_from_pdf(file) -> str:
    """업로드된 PDF 파일에서 텍스트를 추출하는 함수"""
    try:
        with pdfplumber.open(file) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except Exception as e:
        print(f"❌ PDF 텍스트 추출 오류: {e}")
        return ""

# GPT를 사용하여 면접 질문 생성
def generate_interview_question(resume_text: str) -> dict:
    """이력서를 분석하여 GPT로 면접 질문을 생성하는 함수"""
    # 이력서 텍스트가 너무 길면 앞부분만 사용
    resume_text_truncated = resume_text[:4000] if len(resume_text) > 4000 else resume_text
    
    system_content = "You are an AI interview assistant specializing in technical questions. You must return only a valid JSON object with the exact structure as requested."

    user_prompt = f"""
    다음은 한 지원자의 이력서 내용입니다. 이를 분석하여 기술 면접 질문을 1개만 생성해주세요.

    - 질문은 전문적이며 실무 능력을 평가할 수 있어야 합니다.
    - 반드시 JSON 형식으로만 출력하세요. 추가적인 설명을 포함하지 마세요.
    - **"question" 키가 한 번만 사용되도록 하세요.**
    
    JSON 응답 예시는 다음과 같습니다:

    {{
      "question": {{
        "questiontext": "이 직무에 지원하게 된 동기는 무엇인가요?",
        "questiontype": "일반질문"
      }},
      "answer": {{
        "answertext": ""
      }}
    }}
    - answer는 기본적으로 빈 문자열입니다.
    - questiontype은 무조건 일반 질문으로 출력하세요.
    위와 같은 형식을 유지하면서, 다음 이력서를 분석하고 동일한 JSON 구조로만 응답하세요.

    {resume_text_truncated}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )

        raw_output = response.choices[0].message.content.strip()
        
        # GPT가 코드 블록을 반환하는 경우 제거
        raw_output = re.sub(r"```json\s*|\s*```", "", raw_output).strip()
        
        # JSON 변환 시도
        json_output = json.loads(raw_output)

        # 중첩된 "question" 키 제거 (중복된 경우 자동 수정)
        while "question" in json_output and isinstance(json_output["question"], dict):
            if "questiontext" in json_output["question"]:
                break  # 정상적인 구조면 유지
            json_output = json_output["question"]  # 중첩된 경우 한 단계 제거
        
        # 필요한 키가 없는 경우 기본값 설정
        if "question" not in json_output:
            json_output["question"] = {"questiontext": "직무 경험과 관련된 질문을 해주세요.", "questiontype": "일반질문"}
        
        if "questiontext" not in json_output["question"]:
            json_output["question"]["questiontext"] = "직무 경험과 관련된 질문을 해주세요."
            
        if "questiontype" not in json_output["question"]:
            json_output["question"]["questiontype"] = "일반질문"
            
        if "answer" not in json_output:
            json_output["answer"] = {"answertext": ""}
            
        # 최종 응답 반환
        return {
            "question": {
                "questiontext": json_output["question"]["questiontext"],
                "questiontype": json_output["question"]["questiontype"]
            },
            "answer": {
                "answertext": json_output.get("answer", {}).get("answertext", "")
            }
        }

    except (json.JSONDecodeError, KeyError):
        # JSON이 아닌 경우 텍스트에서 질문 형태 추출 시도
        if "?" in raw_output:
            # 물음표가 있는 문장 찾기
            sentences = re.split(r'[.!?]', raw_output)
            for sentence in sentences:
                if "?" in sentence:
                    return {
                        "question": {
                            "questiontext": sentence.strip(),
                            "questiontype": "일반질문"
                        },
                        "answer": {
                            "answertext": ""
                        }
                    }
    
        # 그래도 못 찾으면 전체 텍스트 사용
        return {
            "question": {
                "questiontext": raw_output.replace("\n", " ")[:200],
                "questiontype": "일반질문"
            },
            "answer": {
                "answertext": ""
            }
        }
    
    except Exception as e:
        return {
            "question": {
                "questiontext": "기술적 역량을 평가할 수 있는 질문을 해주세요.",
                "questiontype": "일반질문"
            },
            "answer": {
                "answertext": ""
            }
        }
