# meta developer: @kotcheat
# СОЗДАНО ДЛЯ t.me/KOTmodule

import random
import string
import asyncio
import io
import json
import time
from datetime import datetime
from .. import loader, utils
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel

# ═══════════════════════════════════════════════════════════════════════════
# 💧 WATERMARK: Создано для t.me/KOTmodule | Все права защищены
# ═══════════════════════════════════════════════════════════════════════════

@loader.tds
class KOTpassfolder(loader.Module):
    """🔐 Удобный инструмент для генерации и управления паролями и логинами, который поможет вам создавать безопасные пароли и логины, а также легко управлять ими. Так же можно регулировать длину желаемоего пароля и логина и писать примечание для чего он будет использоваться и многое другое (by @kotcheat | t.me/KOTmodule)"""

    strings = {
        "name": "KOTpassfolder"
    }

    def __init__(self):
        # ═══════════════════════════════════════════════════════════════════
        # 💧 WATERMARK: Инициализация модуля для t.me/KOTmodule
        # ═══════════════════════════════════════════════════════════════════
        self.saved_credentials = []
        self.last_generated_password = None
        self.last_generated_login = None
        self.private_group_id = None
        self.MAX_CREDENTIALS = 15
        self.backup_interval = 86400
        self.last_backup_time = 0
        
        
        self.regular_emojis = {
            "generate": "🎯",
            "save": "💾", 
            "show": "📋",
            "clear": "🧹",
            "note": "📝",
            "delete": "🗑️",
            "add": "➕",
            "edit": "✏️",
            "export": "📤",
            "backup": "💾",
            "restore": "🔄",
            "group": "🔒",
            "file": "📄",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "💡",
            "time": "⏰",
            "protection": "🛡️",
            "stats": "📊",
            "user": "👤",
            "password": "🔑",
            "length": "📏",
            "lock": "🔒",
            "book": "📖",
            "drop": "💧",
            "service": "📝",
            "bullet": "▫️",
            "sosal": "🆔",
            "vremy": "🕐",
            "datag": "📅",
            "otsosal": "👥"
        }
        
        
        self.premium_emojis = {
            "generate": '<emoji document_id=5253617001628181935>👌</emoji>',
            "save": '<emoji document_id=5256094480498436162>📦</emoji>', 
            "show": '<emoji document_id=5255977030322760582>🫂</emoji>',
            "clear": '<emoji document_id=5255831443816327915>🗑</emoji>',
            "note": '<emoji document_id=5253952855185829086>⚙️</emoji>',
            "delete": '<emoji document_id=5253832566036770389>🚮</emoji>',
            "add": '<emoji document_id=5255890718659979335>⬇️</emoji>',
            "edit": '<emoji document_id=5253651477330667400>🎞</emoji>',
            "export": '<emoji document_id=5256182535917940722>⤵️</emoji>',
            "backup": '<emoji document_id=5253671358734281000>📂</emoji>',
            "restore": '<emoji document_id=5253526631221307799>📂</emoji>',
            "group": '<emoji document_id=5256079005731271025>📟</emoji>',
            "file": '<emoji document_id=5256113064821926998>©</emoji>',
            "success": '<emoji document_id=5255813619702049821>✅</emoji>',
            "error": '<emoji document_id=5253864872780769235>❗️</emoji>',
            "warning": '<emoji document_id=5253864872780769235>❗️</emoji>',
            "info": '<emoji document_id=5256230583717079814>📝</emoji>',
            "time": '<emoji document_id=5255971360965930740>🕔</emoji>',
            "protection": '<emoji document_id=5255999175174137421>🛡</emoji>',
            "stats": '<emoji document_id=5253713110111365241>📍</emoji>',
            "user": '<emoji document_id=5292226786229236118>🔄</emoji>',
            "password": '<emoji document_id=5301096984617166561>☝️</emoji>',
            "length": '<emoji document_id=5235588635885054955>🎲</emoji>',
            "lock": '<emoji document_id=5253647062104287098>🔓</emoji>',
            "book": '<emoji document_id=5258466217273871977>💡</emoji>',
            "drop": '<emoji document_id=5257987903945986017>🐈</emoji>',
            "service": '<emoji document_id=5258023599419171861>🔧</emoji>',
            "bullet": '<emoji document_id=5258500422393415126>🎤</emoji>',
            "sosal": '<emoji document_id=5258466470676940666>✈️</emoji>',
            "vremy": '<emoji document_id=5258113901106580375>⌛️</emoji>',
            "datag": '<emoji document_id=5255971360965930740>🕔</emoji>',
            "otsosal": '<emoji document_id=5454371323595744068>🥸</emoji>'
        }

    async def client_ready(self, client, db):
        """Инициализация модуля с восстановлением данных"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Система защиты данных
        # ═══════════════════════════════════════════════════════════════════
        self.db = db
        self.client = client
        
        
        await self._restore_data_with_limit_check()
        
        
        if self.saved_credentials:
            await self._create_backup()

    async def _is_private_chat(self, message):
        """Проверяет, является ли чат приватным"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Проверка типа чата для безопасности
        # ═══════════════════════════════════════════════════════════════════
        try:
            peer = message.peer_id
            return isinstance(peer, PeerUser)
        except:
            return False

    async def _get_emojis(self, user_id):
        """Получает набор эмодзи в зависимости от статуса премиум"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Определение типа аккаунта для эмодзи
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            user = await self.client.get_entity(user_id)
            if hasattr(user, 'premium') and user.premium:
                return self.premium_emojis
            else:
                return self.regular_emojis
        except:
            
            return self.regular_emojis

    def _check_limit_strict(self):
        """СТРОГАЯ проверка лимита записей"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule 
        # ═══════════════════════════════════════════════════════════════════
        current_count = len(self.saved_credentials)
        
        
        if current_count >= self.MAX_CREDENTIALS:
            return "BLOCKED"  
        elif current_count >= self.MAX_CREDENTIALS - 2:
            return "WARNING"  
        else:
            return "OK"  

    def _enforce_limit(self):
        """Принудительно обрезает данные до лимита"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule 
        # ═══════════════════════════════════════════════════════════════════
        if len(self.saved_credentials) > self.MAX_CREDENTIALS:
            
            self.saved_credentials = self.saved_credentials[:self.MAX_CREDENTIALS]
            return True
        return False

    async def _add_credential_safely(self, login, password, service):
        """Безопасно добавляет учётные данные с проверкой лимита"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule
        # ═══════════════════════════════════════════════════════════════════
        
        
        if self._check_limit_strict() == "BLOCKED":
            return False, "LIMIT_EXCEEDED"
        
        
        self.saved_credentials.append((login, password, service))
        
        
        if len(self.saved_credentials) > self.MAX_CREDENTIALS:
            
            self.saved_credentials.pop()
            return False, "LIMIT_EXCEEDED"
        
        
        success = await self._save_data_securely()
        if success:
            return True, "SUCCESS"
        else:
            
            self.saved_credentials.pop()
            return False, "SAVE_ERROR"

    async def _get_strings(self, user_id):
        """Получает строки с соответствующими эмодзи для пользователя"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Динамические строки
        # ═══════════════════════════════════════════════════════════════════
        emojis = await self._get_emojis(user_id)
        
        return {
            "generate_credentials": f"{emojis['generate']} <b>Сгенерированные данные:</b>\n\n"
                                   f"{emojis['user']} <b>Логин:</b> <code>{{login}}</code>\n"
                                   f"{emojis['password']} <b>Пароль:</b> <code>{{password}}</code>\n"
                                   f"{emojis['length']} <b>Длина:</b> {{length}} символов\n"
                                   f"{emojis['stats']} <b>Сохранено записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                                   f"{emojis['protection']} <b>Данные защищены:</b> {emojis['success']}\n\n"
                                   f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "saved_credentials": f"{emojis['show']} <b>Сохраненные учетные данные:</b>\n\n{{credentials}}\n\n"
                               f"{emojis['stats']} <b>Всего записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                               f"{emojis['backup']} <b>Резервных копий:</b> {{backups}}\n"
                               f"{emojis['drop']} <i>Модуль от t.me/KOTmodule</i>\n\n"
                               f"{emojis['time']} <i>Это сообщение будет удалено через 60 секунд.</i>",
            
            "no_saved_credentials": f"{emojis['error']} <b>Нет сохраненных данных</b>\n\n"
                                   f"{emojis['info']} <i>Используйте .gen или .addcred для добавления данных</i>\n\n"
                                   f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "credentials_saved": f"{emojis['success']} <b>Данные надёжно сохранены!</b>\n\n"
                               f"{emojis['stats']} <b>Сохранено записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                               f"{emojis['backup']} <b>Создан бэкап:</b> {{backup_time}}\n\n"
                               f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "credentials_cleared": f"{emojis['clear']} <b>Все данные очищены</b>\n\n"
                                 f"{emojis['backup']} <b>Бэкап сохранён перед очисткой</b>\n\n"
                                 f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "note_added": f"{emojis['note']} <b>Примечание добавлено</b>\n\n"
                         f"{emojis['backup']} <b>Данные защищены резервным копированием</b>\n\n"
                         f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "credentials_deleted": f"{emojis['delete']} <b>Данные удалены</b>\n\n"
                                  f"{emojis['stats']} <b>Осталось записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                                  f"{emojis['backup']} <b>Бэкап обновлён:</b> {{backup_time}}\n\n"
                                  f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "credentials_added": f"{emojis['add']} <b>Учетные данные добавлены</b>\n\n"
                               f"{emojis['user']} <b>Логин:</b> <code>{{login}}</code>\n"
                               f"{emojis['service']} <b>Сервис:</b> {{service}}\n"
                               f"{emojis['stats']} <b>Сохранено записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                               f"{emojis['backup']} <b>Автобэкап:</b> {{backup_time}}\n\n"
                               f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "credentials_edited": f"{emojis['edit']} <b>Данные отредактированы</b>\n\n"
                                f"{emojis['backup']} <b>Изменения сохранены с резервированием</b>\n\n"
                                f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "private_group_created": f"{emojis['group']} <b>Приватная группа создана</b>\n\n"
                                   f"{emojis['otsosal']} <b>Название:</b> {emojis['group']} Хранилище паролей\n"
                                   f"{emojis['sosal']} <b>ID группы:</b> <code>{{chat_id}}</code>\n"
                                   f"{emojis['backup']} <b>ID сохранён в защищённом хранилище</b>\n\n"
                                   f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "private_group_exists": f"{emojis['group']} <b>Приватная группа уже существует</b>\n\n"
                                  f"{emojis['sosal']} <b>ID группы:</b> <code>{{chat_id}}</code>\n\n"
                                  f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "data_recovered": f"{emojis['restore']} <b>Данные восстановлены из резервной копии</b>\n\n"
                             f"{emojis['stats']} <b>Восстановлено записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                             f"{emojis['vremy']} <b>Время бэкапа:</b> {{backup_time}}\n\n"
                             f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "backup_created": f"{emojis['backup']} <b>Резервная копия создана</b>\n\n"
                             f"{emojis['stats']} <b>Records backed up:</b> {{count}}\n"
                             f"{emojis['vremy']} <b>Время:</b> {{backup_time}}\n\n"
                             f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "error": f"{emojis['error']} <b>Произошла ошибка, но данные защищены</b>\n\n"
                    f"{emojis['backup']} <b>Резервные копии целы</b>\n"
                    f"{emojis['info']} <i>Проверьте правильность команды и попробуйте снова</i>\n\n"
                    f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "invalid_index": f"{emojis['error']} <b>Неверный номер записи</b>\n\n"
                            f"{emojis['info']} <i>Используйте .show для просмотра доступных записей</i>\n\n"
                            f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "limit_reached": f"{emojis['warning']} <b>ЛИМИТ ДОСТИГНУТ!</b>\n\n"
                            f"{emojis['stats']} <b>Максимум записей:</b> {self.MAX_CREDENTIALS}/{self.MAX_CREDENTIALS}\n"
                            f"{emojis['error']} <b>ДОБАВЛЕНИЕ ЗАБЛОКИРОВАНО!</b>\n\n"
                            f"{emojis['info']} <b>Действия для продолжения:</b>\n"
                            f"{emojis['bullet']} Удалите ненужные записи: <code>.delcred номер</code>\n"
                            f"{emojis['bullet']} Измените существующие: <code>.editcred номер логин пароль сервис</code>\n"
                            f"{emojis['bullet']} Просмотрите записи: <code>.show</code>\n\n"
                            f"{emojis['backup']} <b>Все данные защищены резервными копиями</b>\n\n"
                            f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "limit_warning": f"{emojis['warning']} <b>ПРЕДУПРЕЖДЕНИЕ О ЛИМИТЕ!</b>\n\n"
                            f"{emojis['stats']} <b>Записей:</b> {{count}}/{self.MAX_CREDENTIALS}\n"
                            f"{emojis['info']} <b>Осталось мест:</b> {{remaining}}\n\n"
                            f"{emojis['time']} <i>Скоро лимит будет достигнут!</i>",
            
            "txt_exported": f"{emojis['file']} <b>TXT файл создан и отправлен</b>\n\n"
                           f"{emojis['stats']} <b>Экспортировано записей:</b> {{count}}\n"
                           f"{emojis['datag']} <b>Дата экспорта:</b> {{date}}\n"
                           f"{emojis['backup']} <b>Копия файла сохранена в резерве</b>\n\n"
                           f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "data_exported": f"{emojis['export']} <b>Данные отправлены в приватную группу</b>\n\n"
                            f"{emojis['backup']} <b>Экспорт записан в журнал защиты</b>\n\n"
                            f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "private_group_not_found": f"{emojis['error']} <b>Приватная группа не создана</b>\n\n"
                                     f"{emojis['info']} <i>Используйте .createprivategroup для создания</i>\n\n"
                                     f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "usage_gen": f"{emojis['book']} <b>Использование команды .gen:</b>\n\n"
                        f"{emojis['bullet']} <code>.gen</code> - генерация с длиной по умолчанию (10)\n"
                        f"{emojis['bullet']} <code>.gen 15</code> - генерация с указанной длиной\n"
                        f"{emojis['bullet']} <i>Максимальная длина: 50 символов</i>\n\n"
                        f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "usage_addcred": f"{emojis['book']} <b>Использование команды .addcred:</b>\n\n"
                            f"{emojis['bullet']} <code>.addcred логин пароль сервис</code>\n"
                            f"{emojis['bullet']} <b>Пример:</b> <code>.addcred myuser mypass123 Gmail</code>\n\n"
                            f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "usage_editcred": f"{emojis['book']} <b>Использование команды .editcred:</b>\n\n"
                             f"{emojis['bullet']} <code>.editcred номер логин пароль сервис</code>\n"
                             f"{emojis['bullet']} <b>Пример:</b> <code>.editcred 1 newuser newpass456 Yahoo</code>\n\n"
                             f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "export_usage": f"{emojis['book']} <b>Использование команды .exportdata:</b>\n\n"
                           f"{emojis['bullet']} <code>.exportdata номер</code> - экспорт конкретной записи\n"
                           f"{emojis['bullet']} <code>.exportdata all</code> - экспорт всех данных\n"
                           f"{emojis['bullet']} <b>Пример:</b> <code>.exportdata 1</code>\n\n"
                           f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>",
            
            "chat_restricted": f"{emojis['warning']} <b>КОМАНДА ЗАБЛОКИРОВАНА В ЧАТАХ!</b>\n\n"
                              f"{emojis['error']} <b>Эта команда содержит конфиденциальные данные</b>\n"
                              f"{emojis['info']} <i>Используйте команду в личных сообщениях с ботом</i>\n\n"
                              f"{emojis['lock']} <b>Доступно только в:</b>\n"
                              f"{emojis['bullet']} Личные сообщения\n"
                              f"{emojis['bullet']} Сохранённые сообщения\n\n"
                              f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>"
        }

    async def _restore_data_with_limit_check(self):
        """Восстанавливает данные с ОБЯЗАТЕЛЬНОЙ проверкой лимита"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Система восстановления данных с ЛИМИТОМ
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            main_data = self.db.get("KOTpassfolder", "saved_credentials", [])
            backup_data = self.db.get("KOTpassfolder", "backup_credentials", [])
            
            
            if self._validate_data(main_data):
                self.saved_credentials = main_data
            elif self._validate_data(backup_data):
                
                self.saved_credentials = backup_data
                self.db.set("KOTpassfolder", "saved_credentials", backup_data)
                await self._log_recovery("backup")
            else:
                
                emergency_backup = self.db.get("KOTpassfolder", "emergency_backup", [])
                if self._validate_data(emergency_backup):
                    self.saved_credentials = emergency_backup
                    self.db.set("KOTpassfolder", "saved_credentials", emergency_backup)
                    await self._log_recovery("emergency")
                else:
                    
                    self.saved_credentials = []
            
            
            if self._enforce_limit():
                
                await self._save_data_securely()
                await self._log_recovery("limit_enforced")
            
            
            self.private_group_id = self.db.get("KOTpassfolder", "private_group_id", None)
            
            
            self._restore_settings()
            
        except Exception as e:
            
            self.saved_credentials = []
            self.private_group_id = None

    def _validate_data(self, data):
        """Проверяет целостность данных С УЧЁТОМ ЛИМИТА"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Валидация данных с лимитом
        # ═══════════════════════════════════════════════════════════════════
        if not isinstance(data, list):
            return False
        
        
        if len(data) > self.MAX_CREDENTIALS:
            return False
        
        for item in data:
            if not isinstance(item, (list, tuple)) or len(item) != 3:
                return False
            if not all(isinstance(x, str) for x in item):
                return False
        
        return True

    def _restore_settings(self):
        """Восстанавливает настройки модуля"""
        try:
            settings = self.db.get("KOTpassfolder", "settings", {})
            
            self.backup_interval = settings.get("backup_interval", 300)
            self.last_backup_time = settings.get("last_backup_time", 0)
        except Exception:
            
            self.backup_interval = 300
            self.last_backup_time = 0

    async def _save_data_securely(self):
        """Безопасно сохраняет данные с множественным резервированием"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Защищённое сохранение данных с проверкой лимита
        # ═══════════════════════════════════════════════════════════════════
        try:
            
            if len(self.saved_credentials) > self.MAX_CREDENTIALS:
                self._enforce_limit()
            
            current_time = time.time()
            
            
            self.db.set("KOTpassfolder", "saved_credentials", self.saved_credentials)
            
            
            self.db.set("KOTpassfolder", "backup_credentials", self.saved_credentials)
            
            
            settings = {
                "backup_interval": self.backup_interval,
                "last_backup_time": current_time
            }
            self.db.set("KOTpassfolder", "settings", settings)
            
            
            if current_time - self.last_backup_time >= self.backup_interval:
                await self._create_emergency_backup()
                self.last_backup_time = current_time
            
            return True
            
        except Exception as e:
            
            try:
                self.db.set("KOTpassfolder", "emergency_backup", self.saved_credentials)
                return True
            except:
                return False

    async def _create_backup(self):
        """Создаёт резервную копию данных"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Система резервного копирования
        # ═══════════════════════════════════════════════════════════════════
        try:
            backup_data = {
                "credentials": self.saved_credentials,
                "private_group_id": self.private_group_id,
                "timestamp": time.time(),
                "version": "2.0",
                "limit": self.MAX_CREDENTIALS,
                "watermark": "t.me/KOTmodule"
            }
            
            
            self.db.set("KOTpassfolder", "backup_1", backup_data)
            self.db.set("KOTpassfolder", "backup_2", backup_data)
            self.db.set("KOTpassfolder", "backup_3", backup_data)
            
            return True
        except Exception:
            return False

    async def _create_emergency_backup(self):
        """Создаёт аварийный бэкап"""
        try:
            emergency_data = {
                "credentials": self.saved_credentials,
                "private_group_id": self.private_group_id,
                "timestamp": time.time(),
                "type": "emergency",
                "limit": self.MAX_CREDENTIALS,
                "source": "t.me/KOTmodule"
            }
            
            self.db.set("KOTpassfolder", "emergency_backup", self.saved_credentials)
            self.db.set("KOTpassfolder", "emergency_full", emergency_data)
            
        except Exception:
            pass

    async def _log_recovery(self, source):
        """Логирует восстановление данных"""
        try:
            recovery_log = self.db.get("KOTpassfolder", "recovery_log", [])
            recovery_log.append({
                "timestamp": time.time(),
                "source": source,
                "records_count": len(self.saved_credentials),
                "limit_enforced": len(self.saved_credentials) <= self.MAX_CREDENTIALS,
                "module_source": "t.me/KOTmodule"
            })
            
            
            if len(recovery_log) > 10:
                recovery_log = recovery_log[-10:]
            
            self.db.set("KOTpassfolder", "recovery_log", recovery_log)
        except Exception:
            pass

    async def _delete_message_after_delay(self, message, delay=30):
        """Удаляет сообщение через указанное время"""
        try:
            await asyncio.sleep(delay)
            if message and hasattr(message, 'delete'):
                await message.delete()
        except Exception:
            pass

    async def _format_credentials_list(self, credentials, user_id):
        """Форматирует список учетных данных для отображения"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Форматирование данных для отображения
        # ═══════════════════════════════════════════════════════════════════
        if not credentials:
            return ""
        
        emojis = await self._get_emojis(user_id)
        
        formatted_list = []
        for index, (login, password, service) in enumerate(credentials):
            service_text = service if service else "Не указан"
            formatted_list.append(
                f"{emojis['show']} <b>#{index + 1}</b>\n"
                f"{emojis['user']} <b>Логин:</b> <code>{login}</code>\n"
                f"{emojis['password']} <b>Пароль:</b> <code>{password}</code>\n"
                f"{emojis['service']} <b>Сервис:</b> {service_text}"
            )
        return "\n\n".join(formatted_list)

    def _generate_txt_content(self):
        """Генерирует содержимое для TXT файла"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Генерация TXT файла
        # ═══════════════════════════════════════════════════════════════════
        if not self.saved_credentials:
            return "Нет сохраненных данных"
        
        content = f"Экспорт учетных данных\nДата: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        content += f"Создано модулем от t.me/KOTmodule\n"
        content += f"Лимит записей: {self.MAX_CREDENTIALS}\n\n"
        content += "=" * 50 + "\n\n"
        
        for index, (login, password, service) in enumerate(self.saved_credentials):
            content += f"Запись #{index + 1}\n"
            content += f"Логин: {login}\n"
            content += f"Пароль: {password}\n"
            content += f"Сервис: {service}\n"
            content += "-" * 30 + "\n\n"
        
        content += f"Всего записей: {len(self.saved_credentials)}/{self.MAX_CREDENTIALS}\n"
        content += "Экспортировано защищённым модулем KOTpassfolder\n"
        content += "Источник: t.me/KOTmodule"
        
        return content

    def _get_backup_count(self):
        """Возвращает количество резервных копий"""
        try:
            count = 0
            for i in range(1, 4):
                if self.db.get("KOTpassfolder", f"backup_{i}", None):
                    count += 1
            return count
        except Exception:
            return 0

    # ═══════════════════════════════════════════════════════════════════════════
    # 💧 КОМАНДЫ МОДУЛЯ - СОЗДАНО ДЛЯ t.me/KOTmodule
    # ═══════════════════════════════════════════════════════════════════════════

    @loader.command(ru_doc="Генерирует случайный пароль и логин")
    async def gen(self, message):
        """🎯 Генерирует случайный пароль и логин"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Команда генерации паролей (ЗАЩИЩЕНА ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                length = 10
            else:
                try:
                    length = int(args)
                    if length <= 0 or length > 50:
                        generated_message = await utils.answer(message, strings["usage_gen"])
                        asyncio.create_task(self._delete_message_after_delay(generated_message))
                        return
                except ValueError:
                    generated_message = await utils.answer(message, strings["usage_gen"])
                    asyncio.create_task(self._delete_message_after_delay(generated_message))
                    return

            
            characters = string.ascii_letters + string.digits + "@$#%&*"
            password = ''.join(random.choices(characters, k=length))
            
            
            login_characters = string.ascii_letters + string.digits
            login = ''.join(random.choices(login_characters, k=length))

            self.last_generated_password = password
            self.last_generated_login = login

            
            await self._save_data_securely()

            generated_message = await utils.answer(
                message, 
                strings["generate_credentials"].format(
                    login=login, 
                    password=password, 
                    length=length,
                    count=len(self.saved_credentials)
                )
            )

            asyncio.create_task(self._delete_message_after_delay(generated_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Добавляет учетные данные вручную")
    async def addcred(self, message):
        """➕ Добавляет учетные данные вручную"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Добавление учётных данных (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                added_message = await utils.answer(message, strings["usage_addcred"])
                asyncio.create_task(self._delete_message_after_delay(added_message))
                return
            
            parts = args.split(maxsplit=2)
            if len(parts) < 2:
                added_message = await utils.answer(message, strings["usage_addcred"])
                asyncio.create_task(self._delete_message_after_delay(added_message))
                return
            
            login = parts[0]
            password = parts[1]
            service = parts[2] if len(parts) > 2 else "Не указан"

            
            success, result = await self._add_credential_safely(login, password, service)
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            backup_time = datetime.now().strftime('%H:%M:%S')

            response_text = strings["credentials_added"].format(
                login=login, 
                service=service, 
                count=len(self.saved_credentials),
                backup_time=backup_time
            )

            
            limit_status = self._check_limit_strict()
            if limit_status == "WARNING":
                remaining = self.MAX_CREDENTIALS - len(self.saved_credentials)
                emojis = await self._get_emojis(user_id)
                response_text += f"\n\n{emojis['warning']} <b>Внимание:</b> Осталось {remaining} мест до лимита!"

            added_message = await utils.answer(message, response_text)
            asyncio.create_task(self._delete_message_after_delay(added_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Редактирует существующие учетные данные")
    async def editcred(self, message):
        """✏️ Редактирует существующие учетные данные"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Редактирование учётных данных (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return
            
            parts = args.split(maxsplit=3)
            if len(parts) < 3:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return
            
            try:
                index = int(parts[0]) - 1
                if index < 0 or index >= len(self.saved_credentials):
                    edited_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(edited_message))
                    return
            except ValueError:
                edited_message = await utils.answer(message, strings["usage_editcred"])
                asyncio.create_task(self._delete_message_after_delay(edited_message))
                return

            login = parts[1]
            password = parts[2]
            service = parts[3] if len(parts) > 3 else "Не указан"

            
            await self._create_backup()

            
            self.saved_credentials[index] = (login, password, service)
            
            
            await self._save_data_securely()

            edited_message = await utils.answer(message, strings["credentials_edited"])
            asyncio.create_task(self._delete_message_after_delay(edited_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Сохраняет последние сгенерированные данные")
    async def save(self, message):
        """💾 Сохраняет последние сгенерированные данные"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Сохранение данных (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if self.last_generated_password is None or self.last_generated_login is None:
                saved_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(saved_message))
                return

            
            success, result = await self._add_credential_safely(
                self.last_generated_login, 
                self.last_generated_password, 
                "Сгенерированные"
            )
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            backup_time = datetime.now().strftime('%H:%M:%S')

            saved_message = await utils.answer(
                message, 
                strings["credentials_saved"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(saved_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Показывает сохраненные данные")
    async def show(self, message):
        """📋 Показывает сохраненные данные"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Отображение сохранённых данных (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if not self.saved_credentials:
                show_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(show_message))
                return

            credentials_list = await self._format_credentials_list(self.saved_credentials, user_id)
            backup_count = self._get_backup_count()
            
            show_message = await utils.answer(
                message, 
                strings["saved_credentials"].format(
                    credentials=credentials_list,
                    count=len(self.saved_credentials),
                    backups=backup_count
                )
            )

            
            asyncio.create_task(self._delete_message_after_delay(show_message, 60))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Генерирует новые данные и сохраняет их")
    async def gensave(self, message):
        """🎯💾 Генерирует новые данные и сохраняет их"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Генерация с автосохранением (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            
            if not args:
                length = 10
            else:
                try:
                    length = int(args)
                    if length <= 0 or length > 50:
                        gensave_message = await utils.answer(message, strings["usage_gen"])
                        asyncio.create_task(self._delete_message_after_delay(gensave_message))
                        return
                except ValueError:
                    gensave_message = await utils.answer(message, strings["usage_gen"])
                    asyncio.create_task(self._delete_message_after_delay(gensave_message))
                    return

            
            characters = string.ascii_letters + string.digits + "@$#%&*"
            password = ''.join(random.choices(characters, k=length))
            login_characters = string.ascii_letters + string.digits
            login = ''.join(random.choices(login_characters, k=length))

            
            success, result = await self._add_credential_safely(login, password, "Сгенерированные")
            
            if not success:
                if result == "LIMIT_EXCEEDED":
                    limit_message = await utils.answer(message, strings["limit_reached"])
                    asyncio.create_task(self._delete_message_after_delay(limit_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                return

            response_text = strings["generate_credentials"].format(
                login=login, 
                password=password, 
                length=length,
                count=len(self.saved_credentials)
            ) + f"\n\n{emojis['success']} <b>Данные автоматически сохранены с резервированием!</b>"

            
            limit_status = self._check_limit_strict()
            if limit_status == "WARNING":
                remaining = self.MAX_CREDENTIALS - len(self.saved_credentials)
                response_text += f"\n\n{emojis['warning']} <b>Внимание:</b> Осталось {remaining} мест до лимита!"

            gensave_message = await utils.answer(message, response_text)
            asyncio.create_task(self._delete_message_after_delay(gensave_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Очищает все сохраненные данные")
    async def clear(self, message):
        """🧹 Очищает все сохраненные данные"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Очистка данных с бэкапом (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            if not self.saved_credentials:
                clear_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(clear_message))
                return

            
            await self._create_backup()

            
            self.saved_credentials.clear()
            
            
            await self._save_data_securely()

            clear_message = await utils.answer(message, strings["credentials_cleared"])
            asyncio.create_task(self._delete_message_after_delay(clear_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Добавляет примечание к сохраненным данным")
    async def note(self, message):
        """📝 Добавляет примечание к сохраненным данным"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Добавление примечаний (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message).split(maxsplit=1)
            if len(args) < 2:
                note_message = await utils.answer(message, 
                                 f"{emojis['book']} <b>Использование:</b>\n\n"
                                 f"{emojis['bullet']} <code>.note номер текст_примечания</code>\n"
                                 f"{emojis['bullet']} <b>Пример:</b> <code>.note 1 Аккаунт для работы</code>\n\n"
                                 f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>")
                asyncio.create_task(self._delete_message_after_delay(note_message))
                return

            try:
                index = int(args[0]) - 1
                note = args[1]
                if index < 0 or index >= len(self.saved_credentials):
                    note_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(note_message))
                    return
            except ValueError:
                note_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(note_message))
                return

            
            await self._create_backup()

            
            login, password, _ = self.saved_credentials[index]
            self.saved_credentials[index] = (login, password, note)
            
            
            await self._save_data_securely()

            note_message = await utils.answer(message, strings["note_added"])
            asyncio.create_task(self._delete_message_after_delay(note_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Удаляет сохраненные данные по номеру")
    async def delcred(self, message):
        """🗑️ Удаляет сохраненные данные по номеру"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Удаление записей с бэкапом (ЗАЩИЩЕНО ОТ ЧАТОВ)
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            
            if not await self._is_private_chat(message):
                restricted_message = await utils.answer(message, strings["chat_restricted"])
                asyncio.create_task(self._delete_message_after_delay(restricted_message))
                return
            
            args = utils.get_args_raw(message)
            if not args:
                delcred_message = await utils.answer(message, 
                                 f"{emojis['book']} <b>Использование:</b>\n\n"
                                 f"{emojis['bullet']} <code>.delcred номер</code>\n"
                                 f"{emojis['bullet']} <b>Пример:</b> <code>.delcred 1</code>\n\n"
                                 f"{emojis['time']} <i>Это сообщение будет удалено через 30 секунд.</i>")
                asyncio.create_task(self._delete_message_after_delay(delcred_message))
                return

            try:
                index = int(args) - 1
                if index < 0 or index >= len(self.saved_credentials):
                    delcred_message = await utils.answer(message, strings["invalid_index"])
                    asyncio.create_task(self._delete_message_after_delay(delcred_message))
                    return
            except ValueError:
                delcred_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(delcred_message))
                return

            
            await self._create_backup()

            
            del self.saved_credentials[index]
            
            
            await self._save_data_securely()
            backup_time = datetime.now().strftime('%H:%M:%S')

            delcred_message = await utils.answer(
                message, 
                strings["credentials_deleted"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(delcred_message))

        except Exception as e:
            
            await self._restore_data_with_limit_check()
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Создает приватную группу")
    async def createprivategroup(self, message):
        """🔒 Создает приватную группу"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Создание приватной группы
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            if self.private_group_id is not None:
                
                try:
                    await self.client.get_entity(self.private_group_id)
                    exists_message = await utils.answer(
                        message, 
                        strings["private_group_exists"].format(chat_id=self.private_group_id)
                    )
                    asyncio.create_task(self._delete_message_after_delay(exists_message))
                    return
                except Exception:
                    
                    self.private_group_id = None

            try:
                
                result = await self.client(CreateChannelRequest(
                    title="🔐 Хранилище паролей",
                    about="Приватное хранилище учетных данных от t.me/KOTmodule",
                    megagroup=True
                ))
                
                if hasattr(result, 'chats') and result.chats:
                    self.private_group_id = result.chats[0].id
                    
                    
                    self.db.set("KOTpassfolder", "private_group_id", self.private_group_id)
                    await self._save_data_securely()
                    
                    created_message = await utils.answer(
                        message, 
                        strings["private_group_created"].format(chat_id=self.private_group_id)
                    )
                    asyncio.create_task(self._delete_message_after_delay(created_message))
                else:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))
                    
            except Exception as e:
                
                try:
                    result = await self.client(CreateChatRequest(
                        users=[],
                        title="🔐 Хранилище паролей"
                    ))
                    
                    if hasattr(result, 'chats') and result.chats:
                        self.private_group_id = result.chats[0].id
                        
                        
                        self.db.set("KOTpassfolder", "private_group_id", self.private_group_id)
                        await self._save_data_securely()
                        
                        created_message = await utils.answer(
                            message, 
                            strings["private_group_created"].format(chat_id=self.private_group_id)
                        )
                        asyncio.create_task(self._delete_message_after_delay(created_message))
                    else:
                        error_message = await utils.answer(message, strings["error"])
                        asyncio.create_task(self._delete_message_after_delay(error_message))
                        
                except Exception:
                    error_message = await utils.answer(message, strings["error"])
                    asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Отправляет данные в приватную группу")
    async def exportdata(self, message):
        """📤 Отправляет данные в приватную группу"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Экспорт данных в группу
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            if self.private_group_id is None:
                export_message = await utils.answer(message, strings["private_group_not_found"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            args = utils.get_args_raw(message)
            if not args:
                export_message = await utils.answer(message, strings["export_usage"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            try:
                if args.lower() == "all":
                    
                    if not self.saved_credentials:
                        export_message = await utils.answer(message, strings["no_saved_credentials"])
                        asyncio.create_task(self._delete_message_after_delay(export_message))
                        return
                    
                    export_text = f"{emojis['group']} <b>Экспорт всех учетных данных</b>\n"
                    export_text += f"{emojis['drop']} <i>Создано модулем от t.me/KOTmodule</i>\n\n"
                    export_text += await self._format_credentials_list(self.saved_credentials, user_id)
                    
                    
                    await self.client.send_message(self.private_group_id, export_text)
                else:
                    
                    try:
                        index = int(args) - 1
                        if index < 0 or index >= len(self.saved_credentials):
                            export_message = await utils.answer(message, strings["invalid_index"])
                            asyncio.create_task(self._delete_message_after_delay(export_message))
                            return
                    except ValueError:
                        export_message = await utils.answer(message, strings["export_usage"])
                        asyncio.create_task(self._delete_message_after_delay(export_message))
                        return

                    login, password, service = self.saved_credentials[index]
                    export_text = (
                        f"{emojis['group']} <b>Экспорт учетных данных #{index + 1}</b>\n"
                        f"{emojis['drop']} <i>Модуль от t.me/KOTmodule</i>\n\n"
                        f"{emojis['user']} <b>Логин:</b> <code>{login}</code>\n"
                        f"{emojis['password']} <b>Пароль:</b> <code>{password}</code>\n"
                        f"{emojis['service']} <b>Сервис:</b> {service}"
                    )
                    
                    
                    await self.client.send_message(self.private_group_id, export_text)

                
                export_message = await utils.answer(message, strings["data_exported"])
                asyncio.create_task(self._delete_message_after_delay(export_message))

            except Exception as e:
                error_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Экспортирует все данные в TXT файл")
    async def exporttxt(self, message):
        """📄 Экспортирует все данные в TXT файл"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Экспорт в TXT
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            emojis = await self._get_emojis(user_id)
            
            if self.private_group_id is None:
                export_message = await utils.answer(message, strings["private_group_not_found"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            if not self.saved_credentials:
                export_message = await utils.answer(message, strings["no_saved_credentials"])
                asyncio.create_task(self._delete_message_after_delay(export_message))
                return

            try:
                
                txt_content = self._generate_txt_content()
                
                
                txt_file = io.BytesIO(txt_content.encode('utf-8'))
                txt_file.name = f"passwords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                
                await self.client.send_file(
                    self.private_group_id,
                    txt_file,
                    caption=f"{emojis['file']} <b>Экспорт учетных данных</b>\n"
                           f"{emojis['drop']} <i>Создано модулем от t.me/KOTmodule</i>\n\n"
                           f"{emojis['stats']} <b>Всего записей:</b> {len(self.saved_credentials)}/{self.MAX_CREDENTIALS}\n"
                           f"{emojis['datag']} <b>Дата:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                           f"{emojis['protection']} <b>Файл защищён резервными копиями</b>"
                )
                
                
                await self._save_data_securely()
                
                export_message = await utils.answer(
                    message, 
                    strings["txt_exported"].format(
                        count=len(self.saved_credentials),
                        date=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
                    )
                )
                asyncio.create_task(self._delete_message_after_delay(export_message))

            except Exception as e:
                error_message = await utils.answer(message, strings["error"])
                asyncio.create_task(self._delete_message_after_delay(error_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Восстанавливает данные из резервной копии")
    async def restore(self, message):
        """🔄 Восстанавливает данные из резервной копии"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 t.me/KOTmodule - Восстановление данных С ПРИНУДИТЕЛЬНОЙ ПРОВЕРКОЙ ЛИМИТА
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            await self._restore_data_with_limit_check()
            
            
            await self._create_backup()
            
            backup_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            restore_message = await utils.answer(
                message,
                strings["data_recovered"].format(
                    count=len(self.saved_credentials),
                    backup_time=backup_time
                )
            )
            asyncio.create_task(self._delete_message_after_delay(restore_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

    @loader.command(ru_doc="Создает ручной бэкап данных")
    async def backup(self, message):
        """💾 Создает ручной бэкап данных"""
        # ═══════════════════════════════════════════════════════════════════
        # 💧 СОЗДАНО ДЛЯ t.me/KOTmodule - Ручное создание бэкапа
        # ═══════════════════════════════════════════════════════════════════
        try:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            
            
            backup_success = await self._create_backup()
            backup_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            if backup_success:
                backup_message = await utils.answer(
                    message,
                    strings["backup_created"].format(
                        count=len(self.saved_credentials),
                        backup_time=backup_time
                    )
                )
            else:
                backup_message = await utils.answer(message, strings["error"])
            
            asyncio.create_task(self._delete_message_after_delay(backup_message))

        except Exception as e:
            user_id = message.sender_id
            strings = await self._get_strings(user_id)
            error_message = await utils.answer(message, strings["error"])
            asyncio.create_task(self._delete_message_after_delay(error_message))

# ═══════════════════════════════════════════════════════════════════════════
# 💧 КОНЕЦ МОДУЛЯ - Создано специально для t.me/KOTmodule
# 🔐 Все права защищены | Водяной знак: t.me/KOTmodule
# ═══════════════════════════════════════════════════════════════════════════
