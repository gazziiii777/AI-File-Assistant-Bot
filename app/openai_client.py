import openai
from config import OPENAI_API_KEY, PROXI
from app.embedding import find_relevant_document, load_documents
import httpx


documents = {}

proxies = PROXI  # Replace with actual proxy
transport = httpx.AsyncHTTPTransport(proxy=proxies)

http_client = httpx.AsyncClient(transport=transport)

client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client  # передаем кастомный HTTP-клиент
)


async def initialize_documents():
    """Загружает документы при старте"""
    global documents
    documents = await load_documents()


async def ask_openai(query):
    """Запрашивает ответ у OpenAI с найденным контекстом"""
    context = await find_relevant_document(query, documents)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
                "content": "Отвечай только на основе предоставленного контекста."},
            {"role": "user", "content": f"Контекст: {context}\nВопрос: {query}"}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


async def generate_question(text):
    """Генерирует вопрос по тексту с помощью GPT"""
    prompt = f"Прочитай этот текст и задай один осмысленный вопрос по нему:\n\n{text}\n\nВопрос:"

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


async def check_answer(question, user_answer, text):
    """Проверяет правильность ответа с помощью GPT"""
    prompt = f"""Текст: {text}

Вопрос: {question}

Ответ пользователя: {user_answer}

Оцени правильность ответа (да или нет), затем кратко объясни почему."""

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
