from fastapi import FastAPI, Response
from gtts import gTTS
import io

app = FastAPI()

@app.post("/tts/")
async def generate_mp3(json_data: dict):
    if not json_data or "questiontext" not in json_data:
        return {"error": "Invalid JSON format. 'questiontext' is required."}

    text = json_data["questiontext"]

    # Generate MP3 using gTTS
    tts = gTTS(text=text, lang="ko")
    mp3_io = io.BytesIO()
    tts.write_to_fp(mp3_io)
    mp3_io.seek(0)  # Reset cursor

    return Response(content=mp3_io.getvalue())
