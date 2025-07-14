import uuid
from io import BytesIO

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from flask import jsonify

from app.utils.config import get

api_key = get("ELEVEN_LABS_IGNA")

def generarVoz(texto):
    load_dotenv()

    elevenlabs = ElevenLabs(
        api_key=api_key,
    )

    audio = elevenlabs.text_to_speech.convert(
        text=texto,
        voice_id="9rvdnhrYoXoUt4igKpBw",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    play(audio)

def stt(ubicacion):
    elevenlabs = ElevenLabs(
        api_key=api_key,
    )

    with open(ubicacion, "rb") as file:
        audio_data = BytesIO(file.read())

    transcription = elevenlabs.speech_to_text.convert(
        file=audio_data,
        model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
        tag_audio_events=True,  # Tag audio events like laughter, applause, etc.
        language_code="spa", # Este siempre sera espaniol porque no trabajaremos en ingles para Proyecto Final
        diarize=True,
    )
    return jsonify({
        "traduccion": transcription.dict()["text"]
    })

def tts(text):
    elevenlabs = ElevenLabs(
        api_key=api_key,
    )

    # Calling the text_to_speech conversion API with detailed parameters
    response = elevenlabs.text_to_speech.convert(
        voice_id="9rvdnhrYoXoUt4igKpBw",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2_5", # use the turbo model for low latency
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )
    # Generating a unique file name for the output MP3 file
    save_file_path = f"{uuid.uuid4()}.mp3"
    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: Audio guardado correctamente!")

    return jsonify({
        "mensaje": "Audio guardado correctamente!",
        "ubicacion": save_file_path
    })