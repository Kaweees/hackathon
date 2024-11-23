from dotenv import load_dotenv
import os
from lmnt.api import Speech
from pprint import pprint
import asyncio
from typing import Dict, Optional
from recorder import record_audio
from IPython.display import Audio

load_dotenv()


def getToken():
    return os.environ.get("LMNT_API_KEY")


LMNT_API_KEY = getToken()


async def list_voices() -> list[Dict]:
    async with Speech(api_key=LMNT_API_KEY) as speech:
        voices = await speech.list_voices()
        pprint(voices)
        return voices


async def get_voice(voice_name: str) -> Optional[str]:
    async with Speech(api_key=LMNT_API_KEY) as speech:
        voices = await speech.list_voices()
        for voice in voices:
            if voice["name"] == voice_name:
                return voice["id"]
        return None


async def create_voice(voice_name: str) -> Dict:
    async with Speech(LMNT_API_KEY) as speech:
        res = await speech.create_voice(
            voice_name,
            enhance=False,
            filenames=["train_audio.wav"],
            type="professional",
        )
        pprint(res)
        return res


async def execute_voice(voice_name: str, text: str) -> Dict:
    voice_id = await get_voice(voice_name)
    if voice_id is None:
        # record_audio("train_audio.wav", duration=30)
        voice_id = await create_voice(voice_name)

    async with Speech(LMNT_API_KEY) as speech:
        res = await speech.synthesize(text, voice_id, format="wav")

        audio_bytes = res["audio"]

        Audio(audio_bytes)
        return res


# Run the async function
if __name__ == "__main__":
    voices = asyncio.run(list_voices())
    asyncio.run(execute_voice("my-new-voice-1", "Hello, how are you?"))
