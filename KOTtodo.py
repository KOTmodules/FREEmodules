# meta developer: @kotcheat

from datetime import datetime
from telethon.tl.types import Message
from .. import loader, utils
import io


@loader.tds
class KOTtodoMod(loader.Module):
    """Простой ToDo планировщик (by @kotcheat)"""

    strings = {
        "name": "KOTtodo",
        "added": "<blockquote><b><emoji document_id=5274055917766202507>🗓</emoji> Задача добавлена</b>\n<b><i>{}</i></b></blockquote>",
        "removed": "<blockquote><b><emoji document_id=5444856076954520455>🧾</emoji> Удалено:</b> <i>{}</i></blockquote>",
        "not_found": "<blockquote><b><emoji document_id=5379999674193172777>🔭</emoji> Задача не найдена</b></blockquote>",
        "empty": "<blockquote><b><emoji document_id=5204284487575285695>🌐</emoji> Список пуст</b></blockquote>",
        "cleared": "<blockquote><b><emoji document_id=5019500511871632068>🗑</emoji> Все задачи удалены</b>\n<i>Удалено задач: {}</i></blockquote>",
        "file_export": "<b><emoji document_id=6111889443193358766>📂</emoji> Список задач экспортирован</b>\n<i>Слишком много задач для отображения</i>",
        "_cls_doc": "Простой ToDo планировщик",
        "_cmd_doc_ktd": "<текст> - Добавить задачу",
        "_cmd_doc_ktdl": "Показать все задачи",
        "_cmd_doc_kutd": "[номер] - Удалить задачу (без номера - удалить все)",
    }

    strings_ru = {
        "added": "<blockquote><b><emoji document_id=5274055917766202507>🗓</emoji> Задача добавлена:</b>\n<b><i>{}</i></b></blockquote>",
        "removed": "<blockquote><b><emoji document_id=5444856076954520455>🧾</emoji> Удалено:</b> <i>{}</i></blockquote>",
        "not_found": "<blockquote><b><emoji document_id=5379999674193172777>🔭</emoji> Задача не найдена</b></blockquote>",
        "empty": "<blockquote><b><emoji document_id=5204284487575285695>🌐</emoji> Список пуст</b></blockquote>",
        "cleared": "<blockquote><b><emoji document_id=5019500511871632068>🗑</emoji> Все задачи удалены</b>\n<i>Удалено задач: {}</i></blockquote>",
        "file_export": "<b><emoji document_id=6111889443193358766>📂</emoji> Список задач экспортирован</b>\n<i>Слишком много задач для отображения</i>",
        "_cls_doc": "Простой ToDo планировщик",
        "_cmd_doc_ktd": "<текст> - Добавить задачу в список",
        "_cmd_doc_ktdl": "Показать все активные задачи",
        "_cmd_doc_kutd": "[номер] - Удалить задачу по номеру (без номера - удалить все задачи)",
    }

    async def client_ready(self, client, db):
        """Инициализация модуля с загрузкой сохраненных данных"""
        self.db = db
        self._client = client
        self.todolist = self.get("ktodo", [])

    async def on_unload(self):
        """Сохранение данных перед выгрузкой модуля"""
        self.set("ktodo", self.todolist)

    async def ktdcmd(self, message: Message):
        """<текст> - Добавить задачу"""
        args = utils.get_args_raw(message)
        
        if not args:
            reply = await message.get_reply_message()
            if reply and reply.text:
                args = reply.text
            else:
                return

        task = {
            "text": args,
            "created": datetime.now().isoformat(),
        }
        
        self.todolist.append(task)
        self.set("ktodo", self.todolist)
        
        await utils.answer(
            message,
            self.strings("added").format(args),
        )

    async def ktdlcmd(self, message: Message):
        """Показать задачи"""
        if not self.todolist:
            await utils.answer(message, self.strings("empty"))
            return

        result = "<b><emoji document_id=5204284487575285695>🌐</emoji> Список задач:</b>\n\n"
        
        total_tasks = len(self.todolist)
        
        
        if total_tasks > 10:
            
            for group_start in range(0, total_tasks, 10):
                group_end = min(group_start + 10, total_tasks)
                
                
                group_text = ""
                for idx in range(group_start, group_end):
                    task = self.todolist[idx]
                    group_text += f"<b>{idx + 1}.</b> <b><i>{task['text']}</i></b>\n"
                
                
                result += f"<blockquote expandable><b><emoji document_id=5274055917766202507>🗓</emoji> Задачи {group_start + 1}-{group_end}</b>\n{group_text}</blockquote>\n"
        else:
            
            for idx, task in enumerate(self.todolist, 1):
                result += f"<blockquote><b>{idx}.</b> <b><i>{task['text']}</i></b></blockquote>\n"

        
        if len(result) > 4000:
            
            file_content = "<emoji document_id=5274055917766202507>🗓</emoji> СПИСОК ЗАДАЧ\n\n"
            for idx, task in enumerate(self.todolist, 1):
                file_content += f"{idx}. {task['text']}\n"
                file_content += f"   Создано: {task['created']}\n\n"
            
            
            file = io.BytesIO(file_content.encode('utf-8'))
            file.name = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            await message.delete()
            await self._client.send_file(
                message.peer_id,
                file,
                caption=self.strings("file_export")
            )
        else:
            await utils.answer(message, result)

    async def kutdcmd(self, message: Message):
        """[номер] - Удалить задачу"""
        args = utils.get_args_raw(message)

        
        if not args:
            count = len(self.todolist)
            if count == 0:
                await utils.answer(message, self.strings("empty"))
                return
            
            self.todolist = []
            self.set("ktodo", self.todolist)
            await utils.answer(message, self.strings("cleared").format(count))
            return

        
        try:
            idx = int(args) - 1
        except (ValueError, TypeError):
            return

        if idx < 0 or idx >= len(self.todolist):
            await utils.answer(message, self.strings("not_found"))
            return

        removed_task = self.todolist.pop(idx)
        self.set("ktodo", self.todolist)
        
        await utils.answer(
            message,
            self.strings("removed").format(removed_task["text"])
        )
