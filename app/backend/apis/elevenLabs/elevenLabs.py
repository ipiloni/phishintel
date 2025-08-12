import os
import uuid
from io import BytesIO

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from flask import jsonify

from app.backend.models.error import responseError
from app.utils.logger import log

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

def tts(data):
    texto = data["texto"]
    idVoz = data["idVoz"]

    if idVoz is None:
        log.warning("No se ha elegido un id de Voz, se utilizara la predeterminada.")
        idVoz = "9rvdnhrYoXoUt4igKpBw"

    try:
        elevenlabs = ElevenLabs(
            api_key=api_key,
        )

        # Calling the text_to_speech conversion API with detailed parameters
        response = elevenlabs.text_to_speech.convert(
            voice_id=idVoz,
            output_format="mp3_22050_32",
            text=texto,
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

        # Ruta absoluta a la carpeta /app/audios
        audios_dir = os.path.join(os.path.dirname(__file__), "audios")
        os.makedirs(audios_dir, exist_ok=True) # Crear la carpeta si no existe

        # Nombre único para el archivo
        save_file_path = os.path.join(audios_dir, f"{uuid.uuid4()}.mp3")

        # Guardar el archivo de audio
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        log.info(f"Audio guardado en: {save_file_path}")

        return jsonify({
            "mensaje": "Audio guardado correctamente!",
            "ubicacion": save_file_path
        })

    except Exception as e:
        log.error("Hubo un error en la llamada a ElevenLabs: " + str(e))
        return responseError("ERROR_ELEVENLABS", "Hubo un error en la llamada a ElevenLabs: " + str(e), 500)