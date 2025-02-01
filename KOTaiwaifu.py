# meta developer: @kotcheat
# scope: hikka_only
# requires: aiohttp>=3.9.3

from hikkatl.types import Message
from .. import loader, utils
from io import BytesIO
import aiohttp
import random

@loader.tds
class KOTaiwaifuMod(loader.Module):
    """Генератор аниме-вайфу (by @kotcheat)"""
    strings = {"name": "KOTaiwaifu"}

    async def client_ready(self, client, db):
        self._client = client

    @loader.command(ru_doc="[теги] - Сгенерировать вайфу")
    async def wafcmd(self, message: Message):
        """Главная команда модуля"""
        args = utils.get_args_raw(message)
        allowed_tags = [
            "maid", "waifu", "marin-kitagawa",
            "mori-calliope", "raiden-shogun",
            "oppai", "selfies", "uniform", "kamisato-ayaka"
        ]
        
        try:
            tags = args.split(",") if args else random.sample(allowed_tags, 2)
            tags = [tag.strip() for tag in tags if tag.strip() in allowed_tags][:2]

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.waifu.im/search",
                    params={"included_tags": tags}
                ) as resp:
                    if resp.status != 200:
                        return await utils.answer(message, "🚫 <b> Ошибка генерации, попробуйте что-то другое! </b> ")
                    data = await resp.json()

                image_url = data["images"][0]["url"]
                async with session.get(image_url) as img_resp:
                    img_data = await img_resp.read()

            await self._client.send_file(
                message.peer_id,
                BytesIO(img_data),
                caption=f"<emoji document_id=5269260681269493579>😳</emoji><b> Ваша вайфу! </b> \n<b><emoji document_id=5305455843846666416>😀</emoji> Теги:</b> {', '.join(tags)}",
                reply_to=message.id
            )
            await message.delete()

        except Exception as e:
            await utils.answer(message, f"🚫 Ошибка: {str(e)}")

    @loader.command(ru_doc="Показать доступные теги") 
    async def tagscmd(self, message: Message):
        """Показывает доступные теги"""
        tags = [
            "maid", "waifu", "marin-kitagawa",
            "mori-calliope", "raiden-shogun",
            "oppai", "selfies", "uniform", "kamisato-ayaka"
        ]
        await utils.answer(
            message,
            f"<emoji document_id=5258380816144154399>😀</emoji><b> Доступные теги: </b> \n{', '.join(tags)}"
        )

version = (1, 0, 1)