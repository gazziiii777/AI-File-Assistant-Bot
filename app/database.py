import aiosqlite
from config import DB_PATH


async def init_db():
    """Создает таблицу для эмбеддингов, если её нет"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                filename TEXT PRIMARY KEY,
                content_hash TEXT,
                embedding BLOB
            )
        """)
        await db.commit()


async def save_embedding(filename, file_hash, embedding):
    """Сохраняет эмбеддинг в БД"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("REPLACE INTO documents (filename, content_hash, embedding) VALUES (?, ?, ?)",
                         (filename, file_hash, embedding.tobytes()))
        await db.commit()


async def get_embedding(filename):
    """Получает эмбеддинг из БД"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT content_hash, embedding FROM documents WHERE filename = ?",
                              (filename,)) as cursor:
            row = await cursor.fetchone()
            return row if row else None
