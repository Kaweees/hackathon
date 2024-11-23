from dotenv import load_dotenv
import os
from lmnt.api import Speech
from pprint import pprint
import asyncio
from typing import Dict, Optional

load_dotenv()

def getToken():
    return os.environ.get("LMNT_API_KEY")

LMNT_API_KEY = getToken()

async def list_voices() -> list[Dict]:
    async with Speech(api_key=LMNT_API_KEY) as speech:
        voices = await speech.list_voices()
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
            type="professional"
        )
        return res

async def execute_voice(voice_name: str, text: str) -> Dict:
    voice_id = await get_voice(voice_name)
    if voice_id is None:
        raise ValueError(f"Voice '{voice_name}' not found")
    
    async with Speech(LMNT_API_KEY) as speech:
        res = await speech.text_to_speech(text, voice_id)
        return res

# Run the async function
if __name__ == "__main__":
    asyncio.run(create_voice("my-new-voice-2"))
    voices = asyncio.run(list_voices())
    pprint(voices)
