import os
import msg_tmp
from pathlib import Path
from uuid import uuid4
from log import pa
import requests
from params import yandex_key, assemblyai_key

def _rec_yandex(audio_path: Path) -> str:
    """
    Convert speech from OGG file to text using Yandex SpeechKit
    
    Args:
        audio_path (str): Path to OGG audio file
        api_key (str): Yandex API key
        
    Returns:
        str: Recognized text
        
    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If API request fails
    """
    api_key = yandex_key    

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    # Validate file extension
    if audio_path.suffix.lower() != '.ogg':
        raise ValueError("File must be in .ogg format")
    
    # API endpoint
    url = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'
    
    # Headers for authentication
    headers = {
        'Authorization': f'Api-Key {api_key}'
    }
    
    # Read audio file
    with open(audio_path, 'rb') as audio_file:
        # Send request to API
        response = requests.post(
            url,
            headers=headers,
            data=audio_file,
            params={
                'format': 'oggopus',
                'lang': 'ru-RU'
            }
        )
    
    # Check response
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")
    
    # Parse response
    result = response.json()
    
    # Return recognized text
    return result.get('result', '')
def _rec_assembly(audio_path):
    import assemblyai as aai

    aai.settings.api_key = assemblyai_key
    config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code='ru')
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(str(audio_path))
 
    return transcript.text

 

async def recognize(msg, answer_func):
    processing_msg = await answer_func(msg_tmp.voice_process, msg)
    try:
        # Получаем ID сообщения для уникальных имен файлов
        save_path = Path('temp/')
        save_path.mkdir(parents=True, exist_ok=True)

        file_name = f"voice_{uuid4()}.ogg"
        file_path = save_path / file_name

        file_id = msg.voice.file_id
        file = await msg.bot.get_file(file_id)
        
        await msg.bot.download_file(file.file_path, file_path)
          
        try:
            text = _rec_yandex(file_path) 
        except: 
            await pa('trying assemblyai')
            text = _rec_assembly(file_path)
             
        os.remove(str(file_path))
        
        await processing_msg.delete()
        
        return str(text)

    except Exception as e:
        await processing_msg.delete()
        await pa(e)
        await pa(e.__class__)
        await answer_func(msg_tmp.voice_error, msg)
        return 400
        
