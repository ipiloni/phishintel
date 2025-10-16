import os
import uuid
from io import BytesIO

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from flask import jsonify
from io import BytesIO

from app.backend.models.error import responseError
from app.utils.logger import log

from app.utils.config import get

api_key = get("ELEVEN_LABS_IGNA")
api_key_2 = get("API_KEY_CLONACION_VOZ")

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
    # TODO: este metodo no lo estamos usando porque Twilio nos esta brindando la respuesta en texto, lo dejamos por las dudas...

    elevenlabs = ElevenLabs(
        api_key=api_key,
    )

    try:
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

    except Exception as e:
        log.error("Hubo un error al generar el STT: " + str(e))
        return responseError("ERROR_ELEVENLABS", "Hubo un error en la llamada a ElevenLabs: " + str(e), 500)

def tts(texto, idVoz, modelId, estabilidad, velocidad, exageracion):

    if estabilidad is not None and (estabilidad < 0.0 or estabilidad > 1.0):
        log.error("La estabilidad debe estar entre 0.0 y 1.0")
        return responseError("PARAMETRO_INVALIDO", "La estabilidad debe estar entre 0.0 y 1.0.", 400)

    if modelId is None:
        modelId = "eleven_flash_v2_5"

    if estabilidad is None:
        estabilidad = 0.5

    if velocidad is None:
        velocidad = 0.6

    try:
        if idVoz is None:
            elevenlabs = ElevenLabs(
                api_key=api_key,
            )
            log.warning("No se ha elegido un id de Voz, se utilizara la predeterminada.")
            idVoz = "O1CnH2NGEehfL1nmYACp"
        else:
            elevenlabs = ElevenLabs(
                api_key=api_key_2
            )

        if modelId == "eleven_multilingual_v2":
            response = elevenlabs.text_to_speech.convert(
                voice_id=idVoz,
                output_format="mp3_22050_32",
                text=texto,
                model_id="eleven_multilingual_v2",

                voice_settings=VoiceSettings(
                    stability=estabilidad,
                    similarity_boost=1.0,
                    style=exageracion,
                    use_speaker_boost=True,
                    speed=velocidad,
                ),
            )
        else:
            response = elevenlabs.text_to_speech.convert(
                voice_id=idVoz,
                output_format="mp3_22050_32",
                text=texto,
                model_id="eleven_flash_v2_5",  # use the turbo model for low latency

                voice_settings=VoiceSettings(
                    stability=estabilidad,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=False,
                    speed=velocidad,
                ),
            )

        # Calling the text_to_speech conversion API with detailed parameters


        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        audios_dir = os.path.join(root_dir, "audios")
        os.makedirs(audios_dir, exist_ok=True) # Crear la carpeta si no existe

        # Nombre único para el archivo
        idAudio = uuid.uuid4()
        save_file_path = os.path.join(audios_dir, f"{idAudio}.mp3")

        # Guardar el archivo de audio
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

        log.info(f"Audio guardado en: {save_file_path}")

        return {
            "mensaje": "Audio guardado correctamente",
            "idAudio": str(idAudio),
            "ubicacion": save_file_path
        }

    except Exception as e:
        log.error("Hubo un error en la llamada a ElevenLabs: " + str(e))
        return responseError("ERROR_ELEVENLABS", "Hubo un error en la llamada a ElevenLabs: " + str(e), 500)

def clonarVoz(ubicacionArchivo, nombreUsuario):
    try:
        load_dotenv()
        elevenlabs = ElevenLabs(
            api_key=api_key_2
        )
        voice = elevenlabs.voices.ivc.create(
            name=nombreUsuario,
            # Replace with the paths to your audio files.
            # The more files you add, the better the clone will be.
            files=[BytesIO(open(ubicacionArchivo, "rb").read())]
        )
        log.info(f"Se creo la voz bajo el ID:{voice.voice_id}")

        if not hasattr(voice, "voice_id") or voice.voice_id is None:
            log.error("No se pudo clonar la voz")
            return responseError("ERROR_ELEVENLABS", "Hubo un error al clonar la voz: " + voice.json(), 500)
        # Puede ser que vaya sin el .dict
        return voice.dict()["voice_id"]
    except Exception as e:
        log.exception("Error al clonar la voz con ElevenLabs")
        return responseError(
            "ERROR_ELEVENLABS",
            f"Excepción al clonar la voz: {str(e)}",
            500
        )