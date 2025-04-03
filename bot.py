import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from config import BOT_TOKEN
from g_ai_utils import generate as gemini


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

message_history = {}
MAX_HISTORY_LENGTH = 6


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    message_history.pop(message.chat.id, None)
    await message.answer(';)')


@dp.message()
async def message_handler(message: Message):
    user_message = message.text
    user_id = message.chat.id
    if user_id not in message_history:
        message_history[user_id] = []

    message_history[user_id].append({'role': 'user', 'parts': user_message})
    ai_response = gemini(history=message_history[user_id])
    message_history[user_id].append({'role': 'model', 'parts': ai_response})
    if len(message_history[user_id]) > MAX_HISTORY_LENGTH:
        message_history[user_id] = message_history[user_id][2:]

    await bot.send_message(chat_id=message.chat.id, text=ai_response)


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
