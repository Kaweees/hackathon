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


async def create_client() -> AsyncElevenLabs:
    return AsyncElevenLabs(api_key=getToken())


async def list_models(client: AsyncElevenLabs) -> List[Dict]:
    response = await client.models.get_all()
    pprint(response)
    return


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
    files: List[str] = []
    i: int = 0
    if os.path.isdir(voice_name):
        for file in os.listdir(voice_name):
            i += 1
            if i > 25:
                break
            files.append(os.path.join(voice_name, file))
    else:
        files.append("coast_guard.wav")
        if not os.path.exists("coast_guard.wav"):
            # Record the training audio if it doesn't exist
            record_audio("coast_guard.wav", duration=30)

    res = await client.clone(
        name=voice_name,
        description="",
        files=files,
        labels=(),
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
    audio_bytes = b""
    async for chunk in audio_generator:
        audio_bytes += chunk

    play(audio_bytes)

    with open("output.wav", "wb") as f:
        f.write(audio_bytes)


# Run the async function
if __name__ == "__main__":
    client = create_client()
    # asyncio.run(list_models(client))
    asyncio.run(
        execute_voice(
            client,
            "coast-guard",
            "Hello, how are you?",
        )
    )
