from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.consts import TOPIC_NAME, USER_QUESTIONS
from bot.file_handlers import input_file
from bot.states import Form
from bot.topics import topics

router = Router()


async def choice_topic(callback_query: CallbackQuery, state: FSMContext,
                       current_topic):
    await callback_query.answer(text=f'Selected topic: '
                                     f'{current_topic.name_topic}')
    await callback_query.message.answer(
        "Thank you. Hurry up to send an answer to a question by pressing a key "
        "'ENTER' before time expires, otherwise no response "
        "will be counted. If you are ready, enter your First and Last Name "
        "after a short pause the survey will begin:")

    questions = input_file(current_topic.file_name)
    await state.update_data({TOPIC_NAME: current_topic.name_topic,
                             USER_QUESTIONS: questions})
    await state.set_state(Form.username)


for topic in topics:
    @router.callback_query(Form.choice_topic, F.data == topic.data_topic)
    async def handler(callback_query: CallbackQuery, state: FSMContext,
                      current_topic=topic):
        await choice_topic(callback_query, state, current_topic)
