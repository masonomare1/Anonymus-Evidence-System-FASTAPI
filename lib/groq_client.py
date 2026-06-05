import io

from groq import Groq

from lib.env import get_groq_api_key


def create_groq_client(api_key=None):
    key = api_key if api_key is not None else get_groq_api_key()
    groq = Groq(api_key=key)

    def complete(messages):
        res = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=1500,
        )
        return (res.choices[0].message.content if res.choices else None) or ""

    def transcribe(audio_bytes):
        file_obj = io.BytesIO(audio_bytes)
        file_obj.name = "audio.mp3"
        res = groq.audio.transcriptions.create(
            file=file_obj,
            model="whisper-large-v3",
        )
        return res.text or ""

    return {"complete": complete, "transcribe": transcribe}
