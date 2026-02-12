from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional
import logging
import aiomax
import aiohttp
import asyncio
from contextlib import asynccontextmanager

from config.config import config
from handlers.start import router

# Логирование
logger = logging.getLogger(__name__)

# Токен бота
bot = aiomax.Bot(config.BOT_TOKEN)

# Роутеры бота
bot.add_router(router)

# Лайфспан
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Создаем сессию бота
    print("Инициализация сессии бота...")
    bot.session = aiohttp.ClientSession()
    print("Инициализация сессии прошла удачно!")

    # Отправка вебхук ссылки для получения уведомлений
    print("Отправляем вебхук ссылку...")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://platform-api.max.ru/subscriptions",
            headers={
                "Authorization": config.BOT_TOKEN,
                "Content-Type": "application/json"
            },
            json={
                "url": config.WEBHOOK_URL+"/webhook",
                "update_types": ["message_created", "message_callback", "bot_started"],
                "secret": config.WEBHOOK_SECRET
            }
        ) as resp:
            result = await resp.json()
            print(f"Webhook установлен: {result}")
    
    yield
    # Удаляем вебхук ссылку
    print("Отключение бота...")
    async with aiohttp.ClientSession() as session:
        async with session.delete(
            "https://platform-api.max.ru/subscriptions",
            headers={"Authorization": config.BOT_TOKEN}
        ) as resp:
            print("Webhook удалён.")
    
    # Разрываем сессию бота
    if bot.session:
        await bot.session.close()
        print("Сессия бота закрыта.")

# Вебхук эндпоинт для получения сообщений
app = FastAPI(lifespan=lifespan)
@app.post("/webhook")
async def webhook(request: Request, x_max_bot_api_secret: Optional[str] = Header(None)):
    if x_max_bot_api_secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    update_data = await request.json()
    asyncio.create_task(bot.handle_update(update_data))
    
    return {"ok": True}


if __name__ == "__main__":
    print("Запуск веб-сервера...")
    import uvicorn
    uvicorn.run(app, host=config.WEBHOOK_HOST, port=config.WEBHOOK_PORT, log_level="debug")
    print("Веб-сервер выключен.")