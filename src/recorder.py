import pyaudio
import wave

def record_audio(filename, duration=5, sample_rate=44100, channels=1, chunk=1024):
    """
    Record audio from microphone and save as WAV file
    
    Args:
        filename (str): Output WAV file path
        duration (int): Recording duration in seconds
        sample_rate (int): Audio sample rate
        channels (int): Number of audio channels (1=mono, 2=stereo)
        chunk (int): Number of frames per buffer
    """
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    
    # Open audio stream
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk
    )
    
    print("* Recording...")
    
    # Record audio frames
    frames = []
    for _ in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)
    
    print("* Done recording")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save to WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
