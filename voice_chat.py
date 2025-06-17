import requests
import json
import pyaudio
import wave
import numpy as np
import time
from gtts import gTTS
import os
from playsound import playsound

# API Keys and URLs - Only Deepgram is directly used here now for transcription
# GEMINI_API_KEY = "AIzaSyCBQSpRAR1Ua-nrTd_hAg2ohc195ceNhBk" # This is now handled in config.py and ai_service.py
DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")  # Use environment variable
# GEMINI_URL is now handled in ai_service.py
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"

# Audio settings
CHANNELS = 1
SAMPLE_RATE = 24000
FORMAT = pyaudio.paInt16
CHUNK = 1024

# End phrases to stop the conversation
END_PHRASES = [
    "goodbye",
    "bye",
    "see you",
    "thank you",
    "that's all",
    "stop",
    "exit",
    "quit",
    "end",
    "finish"
]

# SYSTEM_PROMPT is now handled in ai_service.py
# SYSTEM_PROMPT = """You are a concise AI assistant. Follow these rules strictly:
# 1. Always respond in 1-2 sentences maximum
# 2. Use plain text only - no markdown, no special characters, no formatting
# 3. No prefixes or suffixes - just the direct answer
# 4. No bullet points, no lists, no quotes
# 5. Keep it simple and straightforward"""

def record_audio(filename="recording.wav", silence_threshold=0.01, silence_duration=2):
    """Record audio from microphone and save to WAV file. This function is not used by the frontend JS anymore."""
    # This function is now deprecated in favor of browser-side recording
    # and silence detection for full-duplex functionality.
    # Original recording logic (kept for reference, but not active):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=SAMPLE_RATE,
                   input=True,
                   frames_per_buffer=CHUNK)
    
    frames = []
    silent_chunks = 0
    silent_chunks_threshold = int(silence_duration * SAMPLE_RATE / CHUNK)
    
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        
        audio_data = np.frombuffer(data, dtype=np.int16)
        rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
        
        if rms < silence_threshold * 32768:
            silent_chunks += 1
        else:
            silent_chunks = 0
            
        if silent_chunks >= silent_chunks_threshold:
            break
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filename

def transcribe_audio(filename):
    """Transcribe audio file using Deepgram API."""
    headers = {
        'Authorization': f'Token {DEEPGRAM_API_KEY}',
        'Content-Type': 'audio/wav'
    }
    
    with open(filename, 'rb') as audio:
        response = requests.post(DEEPGRAM_URL, headers=headers, data=audio)
        
    if response.status_code == 200:
        result = response.json()
        return result['results']['channels'][0]['alternatives'][0]['transcript']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# ask_gemini is now handled in ai_service.py as ask_gemini_with_context
# def ask_gemini(question):
#     """Send a question to Gemini and get the response."""
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     
#     data = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": f"{SYSTEM_PROMPT}\n\nQuestion: {question}"
#                     }
#                 ]
#             }
#         ]
#     }
#     
#     try:
#         response = requests.post(GEMINI_URL, headers=headers, json=data)
#         response.raise_for_status()
#         
#         result = response.json()
#         if 'candidates' in result and len(result['candidates']) > 0:
#             return result['candidates'][0]['content']['parts'][0]['text']
#         else:
#             return "No response from Gemini"
#             
#     except requests.exceptions.RequestException as e:
#         return f"Error: {str(e)}"

def text_to_speech(text):
    """Convert text to speech using gTTS. This is not used by the frontend JS anymore."""
    # This function is now deprecated in favor of browser-side Speech Synthesis API
    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        temp_file = "temp_speech.mp3"
        tts.save(temp_file)
        
        # Play the audio
        playsound(temp_file)
        
        # Clean up
        os.remove(temp_file)
        return True
    except Exception as e:
        print(f"Error in text to speech: {e}")
        return False

def is_end_phrase(text):
    """Check if the text contains any end phrases. This is not used by the frontend JS anymore."""
    # This function is now deprecated as the frontend handles conversation stopping.
    text = text.lower().strip()
    return any(phrase in text for phrase in END_PHRASES)

# The main function for standalone execution is no longer relevant for the web app integration.
# def main():
#     print("Voice Chat with Gemini (type 'quit' or say 'goodbye' to exit)")
#     print("-" * 40)
#     
#     while True:
#         # Record user's speech
#         audio_file = record_audio()
#         
#         # Transcribe speech to text
#         print("\nTranscribing...")
#         question = transcribe_audio(audio_file)
#         
#         if not question:
#             print("Could not transcribe audio. Please try again.")
#             continue
#             
#         print(f"\nYou said: {question}")
#         
#         # Check for end phrases
#         if is_end_phrase(question):
#             print("\nGoodbye!")
#             break
#         
#         # Get response from Gemini
#         print("\nGetting response from Gemini...")
#         response = ask_gemini(question)
#         print(f"\nGemini: {response}")
#         
#         # Convert response to speech and play it
#         print("\nConverting to speech...")
#         if not text_to_speech(response):
#             print("Failed to convert text to speech")

# if __name__ == "__main__":
#     main()