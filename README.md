# MentorBot

AI‑powered Telegram bot that creates personal mentors and helps you stay on track.

## Features

- Built on [aiogram 3](https://github.com/aiogram/aiogram) and [SQLAlchemy 2](https://www.sqlalchemy.org/)
- Asynchronous PostgreSQL and Redis support
- Easily customizable texts and keyboards
- Optional payment system (toggle via `PROVIDER_ENABLED`)
- Ready for Docker or systemd deployment

## Quick start

### With Docker
1. Copy `.env.example` to `.env` and adjust variables
2. Build and run
   ```sh
   docker-compose up --build -d
   ```

### Manual run
1. Install dependencies
   ```sh
   poetry install
   ```
2. Run migrations
   ```sh
   poetry run alembic upgrade head
   ```
3. Start the bot
   ```sh
   poetry run python -m tgbot
   ```

## Environment variables
See `.env.example` for a full list. Important ones:

- `COMMON_BOT_TOKEN` – Telegram bot token
- `COMMON_ENCRYPTION_KEY` – key for storing private data
- `PROVIDER_ENABLED` – set to `false` to disable payments
- `OPENAI_API_KEY` – OpenAI access token

## License

Distributed under the MIT License. See `LICENSE` for more information.

