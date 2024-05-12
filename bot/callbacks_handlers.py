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
    await callback_query.answer(text=f'Вьбрана тема: '
                                     f'{current_topic.name_topic}')
    await callback_query.message.answer(
        "Спасибо. Успейте отправить ответ на вопрос нажатием клавиши "
        "'ENTER' до истечения времени, в противном случае ответ не "
        "будет засчитан. Если готовы, то введите свою Фамилию и Имя, "
        "после короткой паузы начнётся опрос:")

    questions = input_file(current_topic.file_name)
    await state.update_data({TOPIC_NAME: current_topic.name_topic,
                             USER_QUESTIONS: questions})
    await state.set_state(Form.username)


for topic in topics:
    @router.callback_query(Form.choice_topic, F.data == topic.data_topic)
    async def handler(callback_query: CallbackQuery, state: FSMContext,
                      current_topic=topic):
        await choice_topic(callback_query, state, current_topic)
