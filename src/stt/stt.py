from fastapi import APIRouter, UploadFile, File, HTTPException
from openai import OpenAI
import os
import shutil

router = APIRouter()
client = OpenAI()

UPLOAD_DIR = "uploads"  # 업로드할 폴더
os.makedirs(UPLOAD_DIR, exist_ok=True)  # 폴더 없으면 생성

@router.post("/{user_name}/{answer_id}/answer")
async def post_answer(user_name: str, answer_id: int, file: UploadFile = File(...)):
    if not file.filename.endswith(".wav"):  # 파일 확장자 확인
        raise HTTPException(status_code=400, detail="WAV 파일만 지원됩니다.")

    # 파일 저장 경로 설정
    file_path = os.path.join(UPLOAD_DIR, f"{user_name}_{answer_id}.wav")

    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # OpenAI Whisper API 호출
        with open(file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"
            )

        # 변환된 텍스트 반환
        return {"text": transcription.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT 변환 실패: {str(e)}")

    finally:
        os.remove(file_path)  # 변환 후 파일 삭제 (선택)
