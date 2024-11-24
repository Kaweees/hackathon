from dotenv import load_dotenv
import os
from pprint import pprint
import asyncio
from elevenlabs import play
from typing import Any, Optional, List, Dict
from recorder import record_audio
from elevenlabs.client import AsyncElevenLabs

from IPython.display import Audio

load_dotenv()


def getToken():
    token = os.environ.get("ELEVEN_API_KEY")
    if token is None:
        raise ValueError("ELEVEN_API_KEY not found in environment variables")
    return token


ELEVEN_API_KEY = getToken()


async def list_voices(client: AsyncElevenLabs) -> List[Dict]:
    response = await client.voices.get_all()
    return response.voices


async def get_voice(client: AsyncElevenLabs, voice_name: str) -> Optional[str]:
    voices = await list_voices(client)
    for voice in voices:
        if voice.name == voice_name:
            return voice.voice_id
    return None


async def create_voice(client: AsyncElevenLabs, voice_name: str) -> str:
    # First record the training audio
    if not os.path.exists("train_audio.wav"):
        record_audio("train_audio.wav", duration=30)

    res = await client.clone(
        name=voice_name,
        description="",
        files=["train_audio.wav"],
    )

    pprint(res)
    return res.voice_id


async def execute_voice(client: AsyncElevenLabs, voice_name: str, text: str) -> Dict:
    voice_id = await get_voice(client, voice_name)
    if voice_id is None:
        print("Voice not found. Creating new voice...")
        try:
            voice_id = await create_voice(client, voice_name)
        except Exception as e:
            print(f"Error creating voice: {e}")
            return None

    # Collect all chunks of audio data
    audio_generator = await client.generate(
        text=text, voice=voice_id, model="eleven_multilingual_v2", stream=False
    )
    
    # Convert generator to bytes
    audio_bytes = b''
    async for chunk in audio_generator:
        audio_bytes += chunk

    play(audio_bytes)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)


# Run the async function
if __name__ == "__main__":
    client = AsyncElevenLabs(api_key=ELEVEN_API_KEY)
    asyncio.run(execute_voice(client, "my-new-voice-3", "Hello, how are you?"))
