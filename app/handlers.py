import asyncio
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.openai_client import ask_openai, generate_question_and_answer, check_answer
from app.embedding import load_documents_fragment


class Ask(StatesGroup):
    question = State()


class Quiz(StatesGroup):
    questions = State()  # Хранит список вопросов и правильных ответов
    current_question = State()  # Текущий индекс вопроса
    user_answers = State()  # Ответы пользователя


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Привет!')


@router.message(Command('question'))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Ask.question)
    await message.answer('Привет! Задай свой вопрос')


@router.message(Ask.question)
async def ask_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    data = await state.get_data()
    response = await ask_openai(data['question'])
    await message.answer(response)
    await state.clear()


@router.message(Command('test'))
async def start_quiz(message: Message, state: FSMContext):
    # Генерируем 3 вопроса
    text = await load_documents_fragment()
    questions_answers = []

    for _ in range(3):
        question, answer = await generate_question_and_answer(text)
        questions_answers.append((question, answer))

    # Сохраняем вопросы и начинаем квиз
    await state.set_state(Quiz.questions)
    await state.update_data(
        questions_answers=questions_answers,
        current_question=0,
        user_answers=[]
    )

    # Сразу задаем первый вопрос
    await ask_current_question(message, state)


async def ask_current_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current_idx = data['current_question']
    questions = data['questions_answers']

    if current_idx < len(questions):
        question, _ = questions[current_idx]
        await message.answer(f"Вопрос {current_idx + 1}/{len(questions)}:\n{question}")
        await state.set_state(Quiz.user_answers)
    else:
        # Все вопросы заданы, проверяем ответы
        await check_all_answers(message, state)


@router.message(Quiz.user_answers)
async def process_answer(message: Message, state: FSMContext):
    # Сохраняем ответ пользователя
    data = await state.get_data()
    current_idx = data['current_question']
    user_answers = data['user_answers']
    questions_answers = data['questions_answers']

    user_answers.append(message.text)
    await state.update_data(
        user_answers=user_answers,
        current_question=current_idx + 1
    )

    # Сразу задаем следующий вопрос
    await ask_current_question(message, state)


async def check_all_answers(message: Message, state: FSMContext):
    data = await state.get_data()
    questions_answers = data['questions_answers']
    user_answers = data['user_answers']

    results = []
    for i, ((question, correct_answer), user_answer) in enumerate(zip(questions_answers, user_answers)):
        response = await check_answer(question, user_answer, correct_answer)
        results.append(f"Вопрос {i + 1}:\n{response}\n")

    await message.answer("Результаты теста:\n" + "\n".join(results))
    await state.clear()
