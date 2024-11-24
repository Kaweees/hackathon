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


async def create_voice(voice_name: str) -> str:
    # First record the training audio
    record_audio("train_audio.wav", duration=30)

    async with Speech(LMNT_API_KEY) as speech:
        res = await speech.create_voice(
            voice_name,
            enhance=True,
            filenames=["train_audio.wav"],
            type="professional",
        )
        pprint(res)
        return res["id"]


async def execute_voice(voice_name: str, text: str) -> Dict:
    voice_id = await get_voice(voice_name)
    if voice_id is None:
        print("Voice not found. Creating new voice...")
        try:
            voice_id = await create_voice(voice_name)
            # Wait a few seconds for the voice to be ready
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Error creating voice: {e}")
            # Fallback to a default system voice
            voice_id = "nathan"
    
    async with Speech(LMNT_API_KEY) as speech:
        res = await speech.synthesize(text, voice_id, format="wav")
        
        audio_bytes = res["audio"]
        
        # Save the audio file
        with open("output.wav", "wb") as f:
            f.write(audio_bytes)
        
        return Audio(audio_bytes)


# Run the async function
if __name__ == "__main__":
    voices = asyncio.run(list_voices())
    asyncio.run(execute_voice("my-new-voice-3", "Hello, how are you?"))
