import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
# from redis.asyncio import Redis
from aiogram.enums import ParseMode
from config_data.config import Config, load_config
from handlers import user

logger = logging.getLogger(__name__)

dp = Dispatcher()

async def main():

    config: Config = load_config()

    logging.basicConfig(level=config.log.log_lvl, format=config.log.format)

    logger.info("starting bot")

    bot = Bot(config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


'''
    # Инициализируем хранилище
    storage = RedisStorage(redis=Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        username=config.redis.username,
    ))



    # Передаю данные в диспечер, чтобы удобно вытащить из хендлера
    dp.workflow_data.update()
    # Настраиваем главное меню бота

    # Регистриуем роутеры в диспетчере
    dp.include_router(user.user_router)

    logger.info('Подключаем роутеры')

    # Регистрируем миддлвари
    logger.info('Подключаем миддлвари')

    # Пропускаем накопившиеся апдейты и запускаем polling
# await bot.delete_webhook(drop_pending_updates=True)
# await dp.start_polling(bot)
'''


if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
