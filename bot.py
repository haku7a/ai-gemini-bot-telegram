import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import BOT_TOKEN, MAX_HISTORY_LENGTH, ALLOWED_USER_IDS
from g_ai_utils import generate as gemini


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class AccessState(StatesGroup):
    access_granted = State()


message_history = {}


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    message_history.pop(message.chat.id, None)
    if message.from_user.id in ALLOWED_USER_IDS:
        await message.answer('👍')
        await state.set_state(AccessState.access_granted)
    else:
        await message.answer("У вас нет доступа.")


@dp.message()
async def message_handler(message: Message,  state: FSMContext):
    if await state.get_state() == AccessState.access_granted:
        user_message = message.text
        user_id = message.chat.id
        if user_id not in message_history:
            message_history[user_id] = []

        message_history[user_id].append(
            {'role': 'user', 'parts': user_message})
        ai_response = gemini(history=message_history[user_id])
        message_history[user_id].append(
            {'role': 'model', 'parts': ai_response})
        if len(message_history[user_id]) > MAX_HISTORY_LENGTH:
            message_history[user_id] = message_history[user_id][2:]

        await bot.send_message(chat_id=message.chat.id, text=ai_response)
    else:
        await message.answer('👎')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
