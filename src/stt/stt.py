from fastapi import APIRouter, UploadFile


router = APIRouter()

@router.post("/{user_name}/{answer_id}/answer")
async def post_answer(user_name: str, answer_id: int, file: UploadFile):
    UPLOAD_DIR = "./uploads"

    content = await file.read()
    filename = f"{user_name}_{answer_id}.mp3"
    with open(f"{UPLOAD_DIR}/{filename}", "wb") as f:
        f.write(content)

    return {"filename": filename}