import asyncio

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message

from bot.answer_sender import send_document_to_tg, send_document_to_email
from bot.consts import (FIRST_LAST_NAME, USERNAME, MESSAGES_FOR_DELETE,
                        TIMER, USER_ANSWERS, USER_QUESTIONS_ITER, WAITING_TIME,
                        TIMER_OFFSET, TIME_FOR_NOTICE, ONE_MINUTE_SECONDS,
                        USER_QUESTIONS, MESSAGE_QUESTION,
                        TOPIC_NAME, TEXT, DURATION, CURRENT_QUESTION)
from bot.file_handlers import generate_word_document
from bot.states import Form

router = Router()


@router.message(Form.username)
async def form_nickname(message: Message, state: FSMContext):
    # Обработать полное имя пользователя и подготовиться к заданию вопросов
    data = await state.get_data()

    first_last_name = message.text
    user_questions_iter = iter(data.get(USER_QUESTIONS, None))

    msg_start = await message.answer(f"Спасибо, {first_last_name}. Скоро "
                                     f"будут задаваться вопросы. Удачи!")

    state_data = {
        FIRST_LAST_NAME: first_last_name,
        USERNAME: message.from_user.username,
        USER_ANSWERS: {},
        MESSAGES_FOR_DELETE: [msg_start],
        TIMER: None,
        USER_QUESTIONS_ITER: user_questions_iter
    }

    await state.update_data(state_data)

    await state.set_state(Form.wait)
    await asyncio.sleep(WAITING_TIME)
    await ask_questions(message, state)


async def wait_for_answer(message: Message, state: FSMContext, timeout):
    # Wait for user's answer within a specified time limit
    formatted_time = format_time(timeout)
    timer_message = await message.answer(f"Осталось времени: {formatted_time}")

    data = await state.get_data()
    msgs_for_delete = data.get(MESSAGES_FOR_DELETE, None)
    msgs_for_delete.append(timer_message)

    for seconds_left in range(timeout - TIMER_OFFSET, -1, -TIMER_OFFSET):
        await asyncio.sleep(TIMER_OFFSET)
        formatted_time = format_time(seconds_left)
        await timer_message.edit_text(f"Осталось времени: {formatted_time}")
        if seconds_left == TIME_FOR_NOTICE:
            msg_left = await message.answer(
                "Время истекает... Лучше введите ответ сейчас, "
                "иначе он не будет засчитан!")
            msgs_for_delete.append(msg_left)

    await handle_timeout(message, state, data)


async def handle_timeout(message: Message, state: FSMContext, data):
    question_text = data.get(CURRENT_QUESTION, None)
    data[USER_ANSWERS][question_text] = ""

    msg_over = await message.answer("Время на ответ вышло.")
    await asyncio.sleep(WAITING_TIME)

    data[MESSAGES_FOR_DELETE].extend(
        [msg_over, data.get(MESSAGE_QUESTION, None)])
    await state.update_data({TIMER: None})

    await ask_questions(message, state)


def format_time(timeout):
    minutes, seconds = divmod(timeout, ONE_MINUTE_SECONDS)
    return f"{minutes}:{seconds:02d}"


async def ask_questions(message: Message, state: FSMContext):
    # Ask questions to the user one by one
    data = await state.get_data()

    # Получаем номер следующего вопроса
    question_number = next(data.get(USER_QUESTIONS_ITER), None)

    if question_number is not None:
        await state.set_state(Form.answer)

        data = await state.get_data()
        data_questions = data.get(USER_QUESTIONS, None)
        current_question = data_questions.get(question_number, None)
        data_question = current_question.get(TEXT, None)
        data_duration = current_question.get(DURATION, None)

        await cancel_timer(data.get(TIMER, None))
        await delete_messages(data.get(MESSAGES_FOR_DELETE, None))

        msg_question = await message.answer(data_question,
                                            protect_content=True)
        timer = asyncio.ensure_future(
            wait_for_answer(message, state, data_duration))

        await state.update_data({CURRENT_QUESTION: data_question,
                                 MESSAGE_QUESTION: msg_question,
                                 MESSAGES_FOR_DELETE: [],
                                 TIMER: timer})
    else:
        # All questions have been answered, process user's data
        await stop_iteration_handle(message, state)


async def stop_iteration_handle(message: Message, state: FSMContext):
    data = await state.get_data()
    data_first_last_name = data.get(FIRST_LAST_NAME, None)
    data_username = data.get(USERNAME, None)
    data_topic_name = data.get(TOPIC_NAME, None)
    data_answers = data.get(USER_ANSWERS, None)

    user_info = dict(name=data_first_last_name, username=data_username)

    await cancel_timer(data.get(TIMER))
    await delete_messages(data.get(MESSAGES_FOR_DELETE, None))

    file_name = (f'Ответы от {data_first_last_name} '
                 f'на тему "{data_topic_name}".docx')
    output_file = generate_word_document(user_info, data_answers,
                                         data_topic_name)
    buffered_file = BufferedInputFile(output_file, file_name)

    await send_document_to_email(output_file, file_name)
    await send_document_to_tg(message, buffered_file)

    await state.clear()
    await message.answer(
        "Это был последний вопрос. Спасибо за ваши ответы!")


async def cancel_timer(timer):
    # Cancel the timer if it's active
    if timer:
        timer.cancel()


async def delete_messages(messages):
    # Delete messages from the chat
    for msg in messages:
        try:
            await msg.delete()
        except TelegramBadRequest:
            pass


@router.message(Form.answer)
async def form_answer(message: Message, state: FSMContext):
    # Process user's answer to a question
    msg_answer = message

    data = await state.get_data()
    data_question = data.get(CURRENT_QUESTION, None)
    data[USER_ANSWERS][data_question] = msg_answer.text
    data[MESSAGES_FOR_DELETE].extend(
        [msg_answer, data.get(MESSAGE_QUESTION, None)])

    await ask_questions(message, state)
