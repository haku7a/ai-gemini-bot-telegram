from aiogram import Bot, types


async def set_default_commands(bot: Bot) -> None:
    commands = [
        types.BotCommand(command='/default',
                         description="Базовая модель"),
        types.BotCommand(
            command='/pro', description="Более совершенная модель"),
        types.BotCommand(command='/start',
                         description="Начать новую сессию"),
    ]
    await bot.set_my_commands(commands)
