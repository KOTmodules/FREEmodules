# meta developer: @kotcheat

from .. import loader, utils
import speech_recognition as sr
from pydub import AudioSegment
import io
import os

@loader.tds
class KOTvoicetotextMod(loader.Module):
    """Модуль преобразования голосовых и видео сообщений в текст (by @kotcheat)"""
    strings = {"name": "KOTvoicetotext"}

    async def client_ready(self, client, db):
        self.client = client

    @loader.command(ru_doc="Преобразовать голосовое/видео сообщение в текст")
    async def texcmd(self, message):
        """Преобразовать голосовое или видео сообщение в текст"""
        if not message.is_reply:
            await utils.answer(message, "<emoji document_id=6037630738545774536>❓</emoji> Ответьте на голосовое или видео сообщение!")
            return

        reply_message = await message.get_reply_message()
        
        if not reply_message or (not reply_message.voice and not reply_message.video_note and not reply_message.video):
            await utils.answer(message, "<emoji document_id=6037630738545774536>❓</emoji> Ответьте на голосовое или видео сообщение!")
            return
            
        # Определяем тип медиа для сообщений
        media_type = "голосовое сообщение"
        if reply_message.video_note:
            media_type = "видеосообщение"
        elif reply_message.video:
            media_type = "видео"
            
        # Сообщение о загрузке
        await utils.answer(message, f"<emoji document_id=5325787248363314644>🫥</emoji> Подождите немного...")
        
        try:
            # Скачиваем медиафайл
            media_file = await reply_message.download_media()
            
            # Конвертируем в WAV для распознавания
            audio = AudioSegment.from_file(media_file)
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            # Удаляем временный файл
            if os.path.exists(media_file):
                os.remove(media_file)
            
            # Распознавание речи
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_io) as source:
                audio_data = recognizer.record(source)
                
            try:
                text = recognizer.recognize_google(audio_data, language="ru-RU")
                await utils.answer(message, f"<emoji document_id=5316899638177964496>☁️</emoji>: {text}")
            except sr.UnknownValueError:
                await utils.answer(message, "<emoji document_id=5800887979366944343>#⃣</emoji> Не удалось распознать речь.")
            except sr.RequestError as e:
                await utils.answer(message, f"<emoji document_id=5800887979366944343>#⃣</emoji> Ошибка запроса к сервису распознавания: {e}")
        except Exception as e:
            await utils.answer(message, f"<emoji document_id=5800887979366944343>#⃣</emoji> Произошла ошибка при обработке: {e}")