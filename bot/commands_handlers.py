from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.consts import ADMINS_IDS
from bot.keyboards import build_topics_kb
from bot.states import Form

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Пожалуйста, выбери нужную тему из списка:",
                         reply_markup=build_topics_kb())
    await state.set_state(Form.choice_topic)


@router.message(Command("admin"))
async def set_admin(message: Message):
    admin_id = str(message.chat.id)
    with open(ADMINS_IDS, "r+") as file:
        admin_ids = file.readlines()
        admin_ids = [admin.strip() for admin in admin_ids]

        if admin_id not in admin_ids:
            file.write(f"{admin_id}\n")
            await message.answer("Вы успешно добавлены в рассылку ответов")
            return

        if admin_id in admin_ids:
            admin_ids.remove(admin_id)
            file.seek(0)
            file.truncate(0)
            for ids in admin_ids:
                file.write(f"{ids}\n")
            await message.answer("Вы успешно удалены из рассылки ответов")


