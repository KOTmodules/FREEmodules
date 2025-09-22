# meta developer: @kotcheat

import asyncio
from .. import loader, utils
import re

@loader.tds
class KOTaddOnMod(loader.Module):
    """Модуль для оставления Watermark в конце вашего поста в телеграмм канале (by @kotcheat | t.me/KOTmodule)"""
    
    strings = {
        "name": "KOTadd-on",
        "signature_added": "<b>Подпись добавлена для канала:</b> <code>{}</code>\n<b>Текст подписи:</b> <code>{}</code>\n\n<i>Сообщение будет удалено через 30 секунд</i>",
        "signature_updated": "<b>Подпись обновлена для канала:</b> <code>{}</code>\n<b>Новый текст подписи:</b> <code>{}</code>\n\n<i>Сообщение будет удалено через 30 секунд</i>",
        "signature_exists": "<b>Для канала</b> <code>{}</code> <b>уже существует подпись:</b>\n<code>{}</code>\n\n<b>Используйте</b> <code>.kdel {}</code> <b>для удаления или добавьте другой канал</b>\n\n<i>Сообщение будет удалено через 30 секунд</i>",
        "signature_removed": "<b>Подпись удалена для канала:</b> <code>{}</code>\n\n<i>Сообщение будет удалено через 30 секунд</i>",
        "signature_not_found": "<b>Подпись для канала</b> <code>{}</code> <b>не найдена</b>\n\n<i>Сообщение будет удалено через 30 секунд</i>",
        "no_signatures": "<b>Активных подписей не найдено</b>\n\n<i>Сообщение будет удалено через 60 секунд</i>",
        "signatures_list": "<b>Активные подписи (страница {}/{}):</b>\n\n<i>Сообщение будет удалено через 60 секунд</i>",
        "channel_signature": "<b>Канал:</b> <code><pre>{}</pre></code>\n<b>Подпись:</b> <pre>{}</pre>",
        "invalid_args": "<b>Неверные аргументы команды</b>\n\n<i>Сообщение будет удалено через 30 секунд</i>"
    }

    def __init__(self):
        self.signatures = {}
        
    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.signatures = self.get("signatures", {})

    def save_signatures(self):
        """Сохранить подписи в базу данных"""
        self.set("signatures", self.signatures)

    def extract_source_link(self, signature):
        """Извлекает ссылку из подписи если она есть"""
        
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, signature)
        
        
        username_pattern = r'@[A-Za-z0-9_]+'
        usernames = re.findall(username_pattern, signature)
        
        
        tme_pattern = r't\.me/[A-Za-z0-9_]+'
        tme_links = re.findall(tme_pattern, signature)
        
        sources = []
        if urls:
            sources.extend(urls)
        if tme_links:
            sources.extend([f"https://{link}" for link in tme_links])
        if usernames:
            sources.extend(usernames)
            
        return sources[0] if sources else None

    @loader.watcher(out=True)
    async def watcher(self, message):
        """Следит за сообщениями и добавляет подписи"""
        if not message.text:
            return
        
        chat_id = str(message.chat_id)
        
        if chat_id in self.signatures:
            signature = self.signatures[chat_id]
            if not message.text.endswith(signature):
                new_text = f"{message.text}\n\n{signature}"
                try:
                    await message.edit(new_text)
                except:
                    pass

    async def _send_and_delete(self, message, text, delay=30):
        """Отправляет сообщение и удаляет его через указанное время"""
        sent_message = await utils.answer(message, text)
        await asyncio.sleep(delay)
        try:
            await sent_message.delete()
        except Exception:
            pass

    @loader.command()
    async def kadd(self, message):
        """[ID канала] [текст подписи] - добавить подпись для канала"""
        args = utils.get_args_raw(message)
        if not args:
            await self._send_and_delete(message, self.strings["invalid_args"])
            return
        
        try:
            parts = args.split(" ", 1)
            if len(parts) != 2:
                await self._send_and_delete(message, self.strings["invalid_args"])
                return
            
            chat_id = parts[0].strip()
            signature_text = parts[1].strip()
            
            
            if not (chat_id.startswith("-") or chat_id.isdigit()):
                await self._send_and_delete(message, self.strings["invalid_args"])
                return
            
            
            if chat_id in self.signatures:
                await self._send_and_delete(
                    message,
                    self.strings["signature_exists"].format(
                        chat_id,
                        self.signatures[chat_id],
                        chat_id
                    )
                )
                return
            
            self.signatures[chat_id] = signature_text
            self.save_signatures()
            
            await self._send_and_delete(
                message,
                self.strings["signature_added"].format(chat_id, signature_text)
            )
        except Exception as e:
            await self._send_and_delete(message, self.strings["invalid_args"])

    @loader.command()
    async def kdel(self, message):
        """[ID канала] - удалить подпись для канала"""
        args = utils.get_args_raw(message)
        if not args:
            await self._send_and_delete(message, self.strings["invalid_args"])
            return
        
        chat_id = args.strip()
        
        if chat_id in self.signatures:
            del self.signatures[chat_id]
            self.save_signatures()
            await self._send_and_delete(
                message,
                self.strings["signature_removed"].format(chat_id)
            )
        else:
            await self._send_and_delete(
                message,
                self.strings["signature_not_found"].format(chat_id)
            )

    @loader.command()
    async def klist(self, message):
        """[номер страницы] - список всех подписей"""
        args = utils.get_args_raw(message)
        page = 1
        
        if args and args.isdigit():
            page = int(args)
        
        if not self.signatures:
            await self._send_and_delete(message, self.strings["no_signatures"], 60)
            return
        
        signatures_per_page = 3
        total_signatures = len(self.signatures)
        total_pages = (total_signatures + signatures_per_page - 1) // signatures_per_page
        
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
        start_idx = (page - 1) * signatures_per_page
        end_idx = start_idx + signatures_per_page
        
        signatures_items = list(self.signatures.items())[start_idx:end_idx]
        
        response = self.strings["signatures_list"].format(page, total_pages) + "\n\n"
        
        for i, (chat_id, signature) in enumerate(signatures_items, 1):
            response += f"<b>{start_idx + i}.</b> "
            response += self.strings["channel_signature"].format(chat_id, signature)
            
            
            source = self.extract_source_link(signature)
            if source:
                response += f"\n<b>Источник:</b> <pre>{source}</pre>"
            
            response += "\n\n"
        
        if total_pages > 1:
            response += f"<i>Для следующей страницы:</i> <code>.klist {page + 1}</code>"
        
        await self._send_and_delete(message, response, 60)
