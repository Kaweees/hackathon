from dotenv import load_dotenv
import os
from pprint import pprint
from elevenlabs import play
from typing import Any, Optional, List, Dict
from recorder import record_audio
from elevenlabs.client import ElevenLabs
from IPython.display import Audio

load_dotenv()


def getToken():
    token = os.environ.get("ELEVEN_API_KEY")
    if token is None:
        raise ValueError("ELEVEN_API_KEY not found in environment variables")
    return token


ELEVEN_API_KEY = getToken()


def list_voices(client: ElevenLabs) -> List[Dict]:
    response = client.voices.get_all()
    # Convert response to list of simplified voice dictionaries
    voices = [
        {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "accent": voice.labels.get("accent"),
            "description": voice.labels.get("description"),
            "age": voice.labels.get("age"),
            "gender": voice.labels.get("gender"),
            "use_case": voice.labels.get("use_case"),
            "preview_url": voice.preview_url,
        }
        for voice in response.voices
    ]
    pprint(voices)
    return response.voices


def get_voice(client: ElevenLabs, voice_name: str) -> Optional[str]:
    voices = list_voices(client)
    for voice in voices:
        if voice.name == voice_name:
            return voice.voice_id
    return None


def create_voice(client: ElevenLabs, voice_name: str) -> str:
    # First record the training audio
    if not os.path.exists("train_audio.wav"):
        record_audio("train_audio.wav", duration=30)

    res = client.clone(
        name=voice_name,
        description="",
        files=["train_audio.wav"],
    )

    pprint(res)
    return res.voice_id


def execute_voice(client: ElevenLabs, voice_name: str, text: str) -> Dict:
    voice_id = get_voice(client, voice_name)
    if voice_id is None:
        print("Voice not found. Creating new voice...")
        try:
            voice_id = create_voice(client, voice_name)
        except Exception as e:
            print(f"Error creating voice: {e}")
            return None

    audio = client.generate(
        text=text, voice=voice_id, model="eleven_multilingual_v2", stream=False
    )

    play(audio)


# Run the async function
if __name__ == "__main__":
    client = ElevenLabs(api_key=ELEVEN_API_KEY)
    execute_voice(client, "my-new-voice-3", "Hello, how are you?")
