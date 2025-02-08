import asyncio

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.openai_client import ask_openai, generate_question, check_answer
from app.embedding import load_documents_fragment


class Ask(StatesGroup):
    question = State()


class Question(StatesGroup):
    text = State()
    question = State()
    answer = State()


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Ask.question)
    await message.answer('Првиет! Задай свой вопрос')


@router.message(Ask.question)
async def ask_question(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    data = await state.get_data()
    response = await ask_openai(data['question'])
    await message.answer(response)
    await state.clear()


@router.message(Command('question'))
async def cmd_question(message: Message, state: FSMContext):
    await state.set_state(Question.answer)
    text = await load_documents_fragment()
    question = await generate_question(text)
    await state.update_data(text=text, question=question)
    await message.answer(question)


@router.message(Question.answer)
async def ask_question(message: Message, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()
    response = await check_answer(data['question'], data['answer'], data['text'])
    await message.answer(response)
    await state.clear()
