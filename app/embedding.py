import os
import hashlib
from random import choice


import numpy as np
import aiofiles
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import DATA_DIR
from app.database import save_embedding, get_embedding

# Загружаем модель эмбеддингов
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_file_hash(filepath):
    """Вычисляет хеш файла для проверки изменений"""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


async def load_documents():
    """Загружает файлы и обновляет эмбеддинги при необходимости (асинхронно)"""
    documents = {}

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_DIR, filename)

            # Асинхронно читаем файл
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content = await f.read()

            file_hash = get_file_hash(filepath)
            stored_data = await get_embedding(filename)

            if stored_data and stored_data[0] == file_hash:
                embedding = np.frombuffer(stored_data[1], dtype=np.float32)
            else:
                embedding = model.encode(content)  # Здесь модель работает синхронно
                await save_embedding(filename, file_hash, embedding)

            documents[filename] = {"data": content, "embedding": embedding}

    return documents


async def find_relevant_document(query, documents):
    """Находит наиболее релевантный текст"""
    query_embedding = model.encode(query)
    similarities = {key: cosine_similarity([query_embedding], [doc["embedding"]])[0][0] for key, doc in
                    documents.items()}
    best_match = max(similarities, key=similarities.get)
    return documents[best_match]["data"]


async def load_documents_fragment():
    """Загружает файлы и выбирает случайный фрагмент текста"""
    documents = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_DIR, filename)

            # Читаем файл асинхронно
            async with aiofiles.open(filepath, "r", encoding="utf-8") as f:
                content = await f.read()
                documents.append(content)

    return choice(documents) if documents else None


