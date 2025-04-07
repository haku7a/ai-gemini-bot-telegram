from aiogram import F
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import BOT_TOKEN, MAX_HISTORY_LENGTH, ALLOWED_USER_IDS
from g_ai_utils import generate as gemini
from services.text_splitter import split_into_chunks
import logging

logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class UserMode(StatesGroup):
    default = State()
    pro = State()


async def set_default_commands(bot: Bot):
    commands = [
        types.BotCommand(command='/default',
                         description="Базовая модель"),
        types.BotCommand(
            command='/pro', description="Более совершенная модель"),
        types.BotCommand(command='/start',
                         description="Начать новую сессию"),
    ]
    await bot.set_my_commands(commands)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id in ALLOWED_USER_IDS:
        await state.clear()
        await message.answer('👋')
        await state.set_state(UserMode.default)
        await state.update_data(history=[])

    else:
        await message.answer("У вас нет доступа.")
        await state.clear()


@dp.message(Command("pro", "default"))
async def switch_model(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state not in (UserMode.default, UserMode.pro):
        await message.answer("=> /start.")
        return

    command_text = message.text.split()[0].lower()
    if command_text == '/pro':
        await state.set_state(UserMode.pro)
    elif command_text == '/default':
        await state.set_state(UserMode.default)


@dp.message(F.text, StateFilter(UserMode.default, UserMode.pro))
async def message_handler(message: Message,  state: FSMContext):
    user_message = message.text
    user_id = message.chat.id
    user_data = await state.get_data()
    history = user_data.get('history', [])

    ai_response = "😔"

    history.append(
        {'role': 'user', 'parts': user_message})
    try:
        await bot.send_chat_action(chat_id=user_id, action="typing")
        ai_response = gemini(history=history)
        history.append(
            {'role': 'model', 'parts': ai_response})
    except Exception as e:
        logger.error(f"Gemini failed: {e}")

    if len(history) > MAX_HISTORY_LENGTH:
        history = history[-MAX_HISTORY_LENGTH:]

    await state.update_data(history=history)

    for chunk in split_into_chunks(ai_response, 4096):
        await bot.send_message(chat_id=user_id, text=chunk)


async def main() -> None:
    await set_default_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
