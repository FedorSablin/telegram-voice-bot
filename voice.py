import uuid
import os
import requests
import config

def get_all_voices():
    return [
        {'name': 'Алиса', 'id': 'alena'},
        {'name': 'Олег', 'id': 'ermil'},
        {'name': 'Женя', 'id': 'jane'},
    ]

def generate_audio(text: str, voice: str, format: str = "oggopus"):
    if format not in ["oggopus", "mp3"]:
        raise ValueError("Формат должен быть 'oggopus' или 'mp3'")

    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    headers = {
        "Authorization": f"Bearer {config.yandex_api_key}"
    }
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": voice,
        "format": format
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Yandex TTS API error: {response.status_code}, {response.text}")

    ext = "ogg" if format == "oggopus" else "mp3"
    audio_path = f"audio_{uuid.uuid4().hex}.{ext}"
    with open(audio_path, "wb") as f:
        f.write(response.content)

    return audio_path
