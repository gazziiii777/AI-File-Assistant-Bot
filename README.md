# AI File Assistant Bot

AI File Assistant Bot is a Telegram bot that answers questions based on files stored in the data folder using GPT. It processes and understands file content, providing intelligent responses and interactive learning.

## 🛠️ Technologies Used 
- **Python 🐍** – Core programming language for bot logic and integrations.
- **Aiogram 🤖** – Asynchronous framework for handling Telegram bot interactions.
- **SQLite 💾** – Database for storing file hashes and embeddings.
- **OpenAI GPT 🤖💬** – AI model for answering questions based on file content.
- **Embedding Models 📊** – Converts text into vector representations for efficient search.

## 📂 Directory Structure
The project is organized as follows:
```
AI File Assistant Bot/
├── app/
│ ├── __init__.py
│ ├── database.py
│ ├── embedding.py
│ ├── handlers.py
│ └──openai_client.py
├──data/
│ └── .txt
├── config.py
├── .gitignore
├── embedding.db
├── README.md 
└── run.py
```
## ⚙️ Setup Guide

This guide will help you set up and run the AI File Assistant Bot, which answers questions based on stored text files.

##### 1. Prerequisites
Ensure you have Python 3.8+ installed.
##### 2. Installation
Clone the repository & Install dependencies
```
git clone https://github.com/your-repo/ai-file-assistant-bot.git
cd ai-file-assistant-bot
pip install -r requirements.txt
```
##### 3. Configuration
Create a `config.py` file with the following fields:

```
TOKEN = "your_bot_token"
OPENAI_API_KEY = "your_openai_api_key"
DATA_DIR = "path/to/data"  
DB_PATH = "path/to/your.db"  
```
##### 4. Adding Files
Place your `.txt` documents inside the `data/` folder. These files will be used for answering questions and generating quizzes.

##### 5. Running the Bot
Start the bot with:
```
python run.py
```


