# MentorBot

AI-powered Telegram bot that creates personalized AI mentors to help users achieve their goals through intelligent conversations and guidance.

## 🚀 Features

- **Personalized AI Mentors**: Each user gets a unique AI mentor tailored to their background and goals
- **Intelligent Conversations**: Powered by OpenAI's GPT models with context-aware responses
- **Vector Memory**: Uses Qdrant for semantic search and conversation history
- **Subscription System**: Flexible pricing with free tier and premium subscriptions
- **Modern Architecture**: Built on aiogram 3, SQLAlchemy 2, and async/await patterns
- **Comprehensive Testing**: Full test suite with unit and integration tests
- **Error Handling**: Robust error handling with user-friendly messages
- **Docker Ready**: Easy deployment with Docker and docker-compose

## 🏗️ Architecture

### Core Components

- **Bot Layer**: aiogram 3 handlers for Telegram interactions
- **Service Layer**: AI services, encryption, vector database operations
- **Data Layer**: SQLAlchemy 2 models with async PostgreSQL
- **Storage Layer**: Redis for FSM state, Qdrant for vector embeddings
- **Configuration**: Pydantic-based configuration management

### Key Services

- **OpenAI Integration**: Mentor creation and conversation handling
- **Vector Database**: Semantic search using Qdrant
- **Encryption**: Secure storage of sensitive user data
- **Payment Processing**: Subscription and mentor purchase handling

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Redis 6+
- OpenAI API key

### With Docker (Recommended)

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd mentorbot
   ```

2. Copy environment configuration
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your configuration
   ```bash
   nano .env
   ```

4. Build and run with Docker Compose
   ```bash
   docker-compose up --build -d
   ```

### Manual Installation

1. Install dependencies
   ```bash
   poetry install
   ```

2. Set up environment variables
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Run database migrations
   ```bash
   poetry run alembic upgrade head
   ```

4. Start the bot
   ```bash
   poetry run python -m tgbot
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COMMON_BOT_TOKEN` | Telegram bot token from @BotFather | Yes |
| `COMMON_ENCRYPTION_KEY` | 32-character encryption key | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `POSTGRES_HOST` | PostgreSQL host | Yes |
| `POSTGRES_USER` | PostgreSQL username | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes |
| `POSTGRES_DB` | PostgreSQL database name | Yes |
| `REDIS_HOST` | Redis host | Yes |
| `REDIS_PASSWORD` | Redis password | No |
| `PROVIDER_ENABLED` | Enable payment system | No |
| `PROVIDER_TOKEN` | Payment provider token | If payments enabled |

### Configuration Classes

The bot uses Pydantic for configuration management with the following classes:

- `CommonConfig`: Bot token, admins, encryption settings
- `PostgresConfig`: Database connection parameters
- `RedisConfig`: Redis connection settings
- `ProviderConfig`: Payment system configuration

## 🧪 Testing

The project includes a comprehensive test suite with unit and integration tests.

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/unit/          # Unit tests
poetry run pytest tests/integration/   # Integration tests

# Run with coverage
poetry run pytest --cov=tgbot --cov-report=html

# Use the test runner script
python run_tests.py all
python run_tests.py unit
python run_tests.py integration
python run_tests.py coverage
```

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── fixtures/                # Test data fixtures
│   └── sample_data.py      # Sample data for testing
├── unit/                   # Unit tests
│   ├── test_models.py      # Database model tests
│   ├── test_repositories.py # Repository tests
│   ├── test_handlers.py    # Handler tests
│   └── test_services.py    # Service tests
├── integration/            # Integration tests
│   └── test_bot_workflow.py # End-to-end workflow tests
└── utils.py                # Test utilities and helpers
```

## 📚 API Documentation

### Core Handlers

#### User Registration Flow
1. `/start` - Initialize bot and check user status
2. Background collection - User provides background information
3. Mentor creation - AI generates personalized mentor
4. Conversation mode - User can chat with their mentor

#### Conversation Flow
1. User sends message
2. Vector search for relevant context
3. AI generates mentor response
4. Message stored in database and vector store

### Database Models

#### DBUser
- User profile information
- Subscription status
- Relationship to mentors and conversations

#### DBMentor
- AI-generated mentor personality
- Background and characteristics
- Relationship to user and conversations

#### DBConversationMessage
- Individual conversation messages
- Role (user/assistant)
- Content and metadata

### Services

#### OpenAI Service
- `init_mentor()`: Create personalized mentor
- `reply_from_mentor()`: Generate mentor responses
- `create_embeddings()`: Generate text embeddings

#### Vector Database Service
- `store_message()`: Store message with embeddings
- `retrieve_history()`: Semantic search for context

## 🔧 Development

### Code Quality

The project uses several tools for code quality:

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Coverage**: Code coverage analysis

### Running Linters

```bash
# Format code
poetry run ruff format

# Lint code
poetry run ruff check

# Type checking
poetry run mypy tgbot/
```

### Database Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1
```

## 🚀 Deployment

### Docker Deployment

The project includes Docker configuration for easy deployment:

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Development with hot reload
docker-compose -f docker-compose.dev.yml up
```

### Systemd Service

For systemd deployment, use the provided service file:

```bash
sudo cp systemd/tgbot.service /etc/systemd/system/
sudo systemctl enable tgbot
sudo systemctl start tgbot
```

## 📊 Monitoring

### Logging

The bot uses structured logging with different levels:

- `DEBUG`: Detailed debugging information
- `INFO`: General information about bot operation
- `WARNING`: Warning messages for business logic issues
- `ERROR`: Error messages for service failures
- `CRITICAL`: Critical errors requiring immediate attention

### Health Checks

The bot includes health check endpoints for monitoring:

- Database connectivity
- Redis connectivity
- OpenAI API availability
- Qdrant vector database status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd mentorbot

# Install dependencies
poetry install --with dev

# Set up pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest
```

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🆘 Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Review the test cases for usage examples

## 🔄 Changelog

### v2.0.0 (Current)
- Complete refactoring with professional English comments
- Comprehensive test suite with unit and integration tests
- Improved error handling and logging
- Enhanced configuration management
- Better code structure and maintainability
- Type hints and documentation improvements

### v1.0.0
- Initial release with basic functionality
- AI mentor creation and conversation
- Subscription system
- Docker deployment support

