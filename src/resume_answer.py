from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import pdfplumber
import os
from openai import Client
from config import OPENAI_API_KEY  # OpenAI API 키 설정

router = APIRouter()

MODEL = "gpt-4o"

# 📌 PDF에서 텍스트 추출하는 함수
def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        return text.strip()
    except Exception as e:
        print(f"PDF 텍스트 추출 오류: {e}")
        return None

# 📌 GPT에 질문 요청하는 함수
def generate_interview_question(resume_text):
    system_content = "You are an AI interview assistant specializing in technical questions."
    user_prompt = (
        "다음은 한 지원자의 이력서 내용입니다. 이를 분석하여 기술 면접 질문을 생성해주세요.\n"
        "면접 질문은 전문적이며 실무 능력을 평가할 수 있어야 합니다.\n"
        "답변은 질문만 출력해주세요.\n\n"
        f"{resume_text}"
    )
    
    try:
        client = Client(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"GPT 호출 오류: {e}")
        return None

# 📌 FastAPI 엔드포인트: PDF에서 텍스트 추출 후 GPT 질문 생성
@router.get("/generate_question")
def generate_question_from_pdf():
    file_path = "/workspaces/llm_lillian/src/files/김선화 개발자 이력서.pdf"
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    # 📌 PDF에서 텍스트 추출
    resume_text = extract_text_from_pdf(file_path)
    if not resume_text:
        raise HTTPException(status_code=500, detail="이력서에서 텍스트를 추출할 수 없습니다.")

    # 📌 GPT를 사용하여 질문 생성
    question_text = generate_interview_question(resume_text)
    if not question_text:
        raise HTTPException(status_code=500, detail="면접 질문 생성 실패")

    # 📌 JSON 형태로 반환
    return JSONResponse(content={"question": question_text})

