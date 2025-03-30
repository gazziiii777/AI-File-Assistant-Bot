import os
import hashlib
from random import choice
from typing import Dict, Any, Optional, Tuple

import numpy as np
import aiofiles
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import DATA_DIR
from app.database import save_embedding, get_embedding

# Инициализация модели эмбеддингов (вынесена в константу для удобства изменения)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")


def get_file_hash(filepath: str) -> str:
    """Вычисляет MD5 хеш файла для отслеживания изменений.

    Args:
        filepath: Путь к файлу

    Returns:
        Строка с хешем файла
    """
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


async def load_documents() -> Dict[str, Dict[str, Any]]:
    """Асинхронно загружает документы и обновляет их эмбеддинги при необходимости.

    Returns:
        Словарь с документами, где ключ - имя файла, значение - словарь с данными и эмбеддингом
    """
    documents = {}

    # Создаем список файлов для обработки
    txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

    for filename in txt_files:
        filepath = os.path.join(DATA_DIR, filename)

        try:
            # Асинхронное чтение файла
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content = await f.read()

            file_hash = get_file_hash(filepath)
            stored_data = await get_embedding(filename)

            if stored_data and stored_data[0] == file_hash:
                # Используем сохраненный эмбеддинг
                embedding = np.frombuffer(stored_data[1], dtype=np.float32)
            else:
                # Генерируем новый эмбеддинг
                embedding = model.encode(content)
                await save_embedding(filename, file_hash, embedding)

            documents[filename] = {
                "data": content,
                "embedding": embedding,
                "hash": file_hash
            }

        except Exception as e:
            print(f"Ошибка при обработке файла {filename}: {str(e)}")
            continue

    return documents


async def find_relevant_document(query: str, documents: Dict[str, Dict[str, Any]]) -> str:
    """Находит наиболее релевантный документ для заданного запроса.

    Args:
        query: Текст запроса
        documents: Словарь с документами (результат load_documents)

    Returns:
        Текст наиболее релевантного документа
    """
    print(documents)
    if not documents:
        return ""

    # Получаем эмбеддинг запроса
    query_embedding = model.encode(query)

    # Вычисляем сходство для всех документов
    doc_embeddings = [doc["embedding"] for doc in documents.values()]
    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]

    # Находим индекс документа с максимальным сходством
    best_match_idx = np.argmax(similarities)
    best_match = list(documents.values())[best_match_idx]

    return best_match["data"]


async def load_documents_fragment() -> Optional[str]:
    """Загружает случайный фрагмент текста из доступных документов.

    Returns:
        Случайный фрагмент текста или None, если документы не найдены
    """
    documents = []

    try:
        txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".txt")]

        for filename in txt_files:
            filepath = os.path.join(DATA_DIR, filename)

            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content = await f.read()
                if content.strip():  # Проверяем, что файл не пустой
                    documents.append(content)

    except Exception as e:
        print(f"Ошибка при загрузке документов: {str(e)}")
        return None

    return choice(documents) if documents else None
