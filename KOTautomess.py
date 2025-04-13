# meta developer: @kotcheat

import asyncio
import time
import logging
from datetime import timedelta
from hikka import loader, utils
from hikka.types import Message

logger = logging.getLogger(__name__)

@loader.tds
class KOTautomess(loader.Module):
    """Автоматическая отправка сообщений в выбранный чат по времени ( by @kotcheat )"""
    
    strings = {"name": "KOTautomess"}
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "max_interval", 2592000,
            "Максимальный интервал (30 дней в секундах)",
            "autosave_interval", 300,
            "Интервал автосохранения (секунды)"
        )
        self.tasks = {}
        self.autosave_task = None
        self.db = None

    async def client_ready(self, client, db):
        self._client = client
        self.db = db
        await self._load_tasks()
        self.autosave_task = asyncio.create_task(self._autosave())

    async def _parse_time(self, time_str: str) -> int:
        units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
        seconds = 0
        num = ""
        for c in time_str:
            if c.isdigit():
                num += c
            elif c in units:
                seconds += int(num) * units[c]
                num = ""
            else:
                raise ValueError("Неверный формат времени")
        if num:
            seconds += int(num)
        return seconds if seconds > 0 else 0

    async def _get_chat_entity(self, chat_identifier: str):
        try:
            if chat_identifier.lstrip('-').isdigit():
                return await self._client.get_entity(int(chat_identifier))
            return await self._client.get_entity(chat_identifier)
        except Exception as e:
            logger.error(f"Ошибка чата: {e}")
            raise ValueError("❌ Чат не найден")

    async def _send_loop(self, chat_id: int, text: str, interval: int, task_id: int):
        next_run = time.time()
        try:
            while True:
                try:
                    delay = max(0, next_run - time.time())
                    await asyncio.sleep(delay)
                    
                    await self._client.send_message(chat_id, text)
                    self.tasks[task_id]["sent_count"] += 1
                    await self._save_tasks()
                    
                    next_run = time.time() + interval
                    
                except Exception as e:
                    logger.error(f"Ошибка в задаче #{task_id}: {str(e)}")
                    await asyncio.sleep(5)
                    next_run = time.time() + interval
                    
        except asyncio.CancelledError:
            logger.info(f"Задача #{task_id} отменена")
        finally:
            if task_id in self.tasks:
                del self.tasks[task_id]
                await self._save_tasks()

    async def _save_tasks(self):
        if self.db:
            self.db.set("KOTautomess", "tasks", {
                task_id: {
                    "chat_id": task["chat_id"],
                    "text": task["text"],
                    "interval": task["interval"],
                    "sent_count": task["sent_count"]
                }
                for task_id, task in self.tasks.items()
            })

    async def _load_tasks(self):
        if self.db:
            saved_tasks = self.db.get("KOTautomess", "tasks", {})
            for task_id, task_data in saved_tasks.items():
                try:
                    self.tasks[int(task_id)] = {
                        "chat_id": task_data["chat_id"],
                        "text": task_data["text"],
                        "interval": task_data["interval"],
                        "sent_count": task_data.get("sent_count", 0),
                        "task": asyncio.create_task(
                            self._send_loop(
                                task_data["chat_id"],
                                task_data["text"],
                                task_data["interval"],
                                int(task_id)
                            )
                        )
                    }
                except Exception as e:
                    logger.error(f"Ошибка загрузки задачи #{task_id}: {e}")

    async def _autosave(self):
        while True:
            await asyncio.sleep(self.config["autosave_interval"])
            await self._save_tasks()

    async def messsendcmd(self, message: Message):
        """<интервал> <чат> <текст> - Добавить задачу"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, "❌ Пример: .messsend 1h30m -100123456 Текст")
        
        try:
            time_part = args.split()[0]
            interval = await self._parse_time(time_part)
            args = args[len(time_part):].strip()

            if interval > self.config["max_interval"]:
                raise ValueError(f"❌ Максимальный интервал: {self.config['max_interval']} сек")
            
            parts = args.split(maxsplit=1)
            if len(parts) < 2:
                raise ValueError("❌ Укажите чат и текст")
            
            chat_identifier, text = parts[0], parts[1]
            chat = await self._get_chat_entity(chat_identifier)
            
            task_id = int(time.time() * 1000)
            self.tasks[task_id] = {
                "chat_id": chat.id,
                "text": text,
                "interval": interval,
                "sent_count": 0,
                "task": asyncio.create_task(
                    self._send_loop(chat.id, text, interval, task_id)
                )
            }
            
            await self._save_tasks()
            await utils.answer(
                message,
                f"✅ Задача #{task_id} запущена\n"
                f"⏱ Интервал: {timedelta(seconds=interval)}"
            )
            
        except Exception as e:
            await utils.answer(message, f"⚠️ Ошибка: {str(e)}")

    async def messsendcancmd(self, message: Message):
        """<ID> - Отменить задачу"""
        args = utils.get_args_raw(message)
        if not args.isdigit():
            return await utils.answer(message, "❌ Укажите числовой ID задачи")
        
        task_id = int(args)
        if task_id not in self.tasks:
            return await utils.answer(message, "🚫 Задача не найдена")
        
        self.tasks[task_id]["task"].cancel()
        del self.tasks[task_id]
        await self._save_tasks()
        await utils.answer(message, f"✅ Задача #{task_id} остановлена")

    async def messlistcmd(self, message: Message):
        """Список задач"""
        if not self.tasks:
            return await utils.answer(message, "📭 Нет активных задач")
        
        response = ["📊 Активные задачи:"]
        for task_id, task in self.tasks.items():
            chat_info = await self._get_chat_info_by_id(task["chat_id"])
            response.append(
                f"▫️ ID задачи: #{task_id}\n"
                f"   🕒 Интервал: {timedelta(seconds=task['interval'])}\n"
                f"   📤 Отправок: {task['sent_count']}\n"
                f"   💬 Чат: {chat_info}\n"
                f"   📝 Сообщение: {utils.escape_html(task['text'][:50])}"
                f"{'...' if len(task['text']) > 50 else ''}"
            )
        
        await utils.answer(message, "\n".join(response))

    async def _get_chat_info_by_id(self, chat_id: int) -> str:
        try:
            chat = await self._client.get_entity(chat_id)
            if hasattr(chat, "username"):
                return f"@{chat.username}"
            elif hasattr(chat, "title"):
                return chat.title
            return str(chat_id)
        except:
            return str(chat_id)

    async def on_unload(self):
        if self.autosave_task:
            self.autosave_task.cancel()
        
        for task_id in list(self.tasks.keys()):
            self.tasks[task_id]["task"].cancel()
            del self.tasks[task_id]
        
        await self._save_tasks()