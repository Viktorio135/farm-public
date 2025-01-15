from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers.user_handlers import listen_to_websocket, router as user_router

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация роутеров
dp.include_router(user_router)

async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        listen_to_websocket(bot)
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
