import logging
from lexicon.lexicon_ru import RU
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards.keyboard_utils import keyboard_start_dialog, keyboard_help_dialog, keyboard_answer
from states.states import FSMFillForm
from services.PythonScripts.ai_blanck import main, genQues
import ast
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, WebAppInfo

logger = logging.getLogger("__name__")

user_router = Router()

user_dict: dict[int, dict[str, str | int | bool]] = {}

@user_router.message(CommandStart())
async def command_start(message: Message):
    await message.answer(RU['/start'], reply_markup=keyboard_help_dialog)


@user_router.message(Command('Web'))
async def commandWEB(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📱 Открыть",
        web_app=WebAppInfo(url="https://assasinbaby.github.io/web/web.html")  # Ваш URL
    )
    await message.answer("Нажмите кнопку:", reply_markup=builder.as_markup())
    await state.clear()

@user_router.message(Command('go_test'))
async def goTest(message: Message, state: FSMContext):
    await state.set_state(FSMFillForm.fill_famili)
    await message.answer(text='Введите ваше имя:')
    await state.clear()

@user_router.message(Command('help'))
async def commandHelp(message: Message):
    await message.answer(text='Я умею 😎:\n\n• Проводить тест на выгорание\n•'
                              'Анализировать данные о сотрудниках с целью проверки на выгорание\n• '
                              'Давать советы по борьбе с выгоранием\nЧем могу вам помочь ❔')

@user_router.callback_query(F.data.in_(['help_button']))
async def command_help(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=RU['Начать тест'],
                                     reply_markup=keyboard_start_dialog)
    await state.set_state(FSMFillForm.fill_famili)
    await callback.answer()


@user_router.callback_query(F.data.in_(['start_dialog']))
async def process_dialog(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Введите ваше имя:')
    await state.set_state(FSMFillForm.fill_famili)
    await callback.answer()


@user_router.message(StateFilter(FSMFillForm.fill_famili), F.text.isalpha())
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Введите вашу фамилию:')
    await state.set_state(FSMFillForm.fill_in_chat)


@user_router.message(StateFilter(FSMFillForm.fill_in_chat), F.voice)
async def process_voice_message(message: Message, state: FSMContext):
    file_id = message.voice.file_id
    await message.reply("Вы отправили голосовое сообщение!")


@user_router.message(StateFilter(FSMFillForm.fill_in_chat))
async def process_dialog_gpt(message: Message, state: FSMContext):
    await state.update_data(famili=message.text)
    user_dict[message.from_user.id] = await state.get_data()
    name = user_dict[message.from_user.id]["name"]
    famili = user_dict[message.from_user.id]["famili"]

    logger.info('Начало работы запросы нейронки')

    # Получаем вопросы
    questions_data = genQues()

    # Преобразуем строку в список
    try:
        if isinstance(questions_data, str):
            questions_list = ast.literal_eval(questions_data)
        else:
            questions_list = list(questions_data)
    except Exception as e:
        logger.error(f"Ошибка преобразования вопросов: {e}")
        await message.answer("Ошибка при загрузке вопросов")
        return

    # Сохраняем вопросы и индекс текущего вопроса в состояние
    await state.update_data(questions=questions_list,
                            current_question_index=0,
                            answers={})

    # Отправляем первый вопрос
    await send_next_question(message, state)


async def send_next_question(message: Message, state: FSMContext):
    """Отправляет следующий вопрос пользователю"""
    user_data = await state.get_data()
    current_index = user_data.get('current_question_index', 0)
    questions = user_data.get('questions', [])

    if current_index < len(questions):
        question_text = questions[current_index]
        await message.answer(
            f"Вопрос {current_index + 1}/{len(questions)}:\n\n{question_text}",
            reply_markup=keyboard_answer)
    else:
        # Все вопросы заданы, завершаем опрос
        await finish_questionnaire(message, state)


async def finish_questionnaire(message: Message, state: FSMContext):
    """Завершает опрос и обрабатывает результаты"""
    user_data = await state.get_data()
    answers = user_data.get('answers', {})
    questions = user_data.get('questions', [])

    # Формируем результат
    result_text = "📊 Результаты опроса:\n\n"
    for i, question in enumerate(questions):
        answer = answers.get(i, "Нет ответа")
        result_text += f"{i+1}. {question}\n   Ответ: {answer}\n\n"

    await message.answer(result_text)

    # Получаем анализ от нейронки
    name = user_data.get('name', '')
    famili = user_data.get('famili', '')

    try:
        analysis_result = main(name.capitalize(), famili.capitalize())
        await message.answer(f"🤖 Анализ нейронки:\n\n{analysis_result}")
    except Exception as e:
        logger.error(f"Ошибка при анализе нейронки: {e}")
        await message.answer("Произошла ошибка при анализе данных")

    # Очищаем состояние
    await state.clear()


@user_router.callback_query(F.data.in_(['yes', 'No']))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает ответы на вопросы"""
    user_data = await state.get_data()
    current_index = user_data.get('current_question_index', 0)
    answers = user_data.get('answers', {})

    # Сохраняем ответ
    answer_text = "Да" if callback.data == 'yes' else "Нет"
    answers[current_index] = answer_text

    # Увеличиваем индекс вопроса
    current_index += 1

    # Обновляем состояние
    await state.update_data(current_question_index=current_index,
                            answers=answers)

    # Отправляем следующий вопрос или завершаем
    if current_index < len(user_data.get('questions', [])):
        await send_next_question(callback.message, state)
    else:
        await finish_questionnaire(callback.message, state)

    await callback.answer()


# Дополнительный хендлер для текстовых ответов (на случай если нужна альтернатива)
@user_router.message(StateFilter(FSMFillForm.fill_in_chat), F.text)
async def process_text_answer(message: Message, state: FSMContext):
    """Обрабатывает текстовые ответы на вопросы"""
    user_data = await state.get_data()
    current_index = user_data.get('current_question_index', 0)

    # Если есть активные вопросы, игнорируем текстовые сообщения
    if current_index < len(user_data.get('questions', [])):
        await message.answer(
            "Пожалуйста, используйте кнопки для ответа на вопросы")
        return

    # Если вопросов нет, обрабатываем как обычное сообщение
    await process_dialog_gpt(message, state)
