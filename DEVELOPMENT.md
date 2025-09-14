# Development Guide

This guide provides detailed instructions for developing and contributing to MentorBot.

## 🛠️ Development Setup

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- PostgreSQL 13+
- Redis 6+
- Docker and Docker Compose (optional)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mentorbot
   ```

2. **Install dependencies**
   ```bash
   poetry install --with dev
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up pre-commit hooks (optional)**
   ```bash
   poetry run pre-commit install
   ```

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite with multiple test categories:

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

### Test Categories

#### Unit Tests (`tests/unit/`)
- **test_models.py**: Database model tests
- **test_repositories.py**: Repository CRUD operations
- **test_handlers.py**: Bot message handlers
- **test_services.py**: AI services and utilities

#### Integration Tests (`tests/integration/`)
- **test_bot_workflow.py**: End-to-end user journeys

### Writing Tests

#### Unit Test Example
```python
@pytest.mark.asyncio
async def test_user_creation(test_repository: Repository):
    """Test creating a new user."""
    user_data = {
        "name": "Test User",
        "telegram_id": "123456789",
    }
    
    user = await test_repository.users.create(DBUser(**user_data))
    
    assert user.id is not None
    assert user.name == "Test User"
    assert user.telegram_id == "123456789"
```

#### Integration Test Example
```python
@pytest.mark.asyncio
async def test_complete_user_registration_flow(test_repository: Repository):
    """Test complete registration flow for a new user."""
    # Test the entire flow from /start to mentor creation
    pass
```

### Test Fixtures

The project provides several fixtures for testing:

- `test_engine`: In-memory SQLite database
- `test_session`: Database session
- `test_repository`: Repository instance
- `test_bot`: Mock Telegram bot
- `test_dispatcher`: Bot dispatcher
- `mock_openai_service`: Mock OpenAI responses
- `sample_user_data`: Sample user data

## 🔍 Code Quality

### Linting and Formatting

```bash
# Format code with Ruff
poetry run ruff format

# Lint code with Ruff
poetry run ruff check

# Fix auto-fixable issues
poetry run ruff check --fix
```

### Type Checking

```bash
# Run MyPy type checking
poetry run mypy tgbot/

# Run with strict mode
poetry run mypy tgbot/ --strict
```

### Code Coverage

```bash
# Generate coverage report
poetry run pytest --cov=tgbot --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

## 🗄️ Database Management

### Migrations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# Show migration history
poetry run alembic history
```

### Database Schema

The project uses SQLAlchemy 2 with the following models:

- **DBUser**: User profile and subscription information
- **DBMentor**: AI-generated mentor personalities
- **DBConversationMessage**: Conversation history

## 🚀 Running the Bot

### Development Mode

```bash
# Run with auto-reload
poetry run python -m tgbot

# Run with debug logging
LOG_LEVEL=DEBUG poetry run python -m tgbot
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f tgbot
```

## 📝 Code Style

### Python Style Guide

The project follows PEP 8 with some modifications:

- Line length: 100 characters
- Use type hints for all functions
- Use docstrings for all public functions
- Use async/await for asynchronous operations

### Naming Conventions

- **Classes**: PascalCase (e.g., `DBUser`, `ErrorHandler`)
- **Functions**: snake_case (e.g., `create_mentor`, `handle_error`)
- **Variables**: snake_case (e.g., `user_id`, `conversation_history`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MODEL`, `MAX_TOKENS`)

### Documentation

- Use Google-style docstrings
- Include type hints for all parameters and return values
- Document exceptions that functions may raise
- Include usage examples in docstrings

## 🐛 Debugging

### Logging

The project uses structured logging with different levels:

```python
from tgbot.misc.logger import logger

# Debug information
logger.debug("Detailed debugging information")

# General information
logger.info("General information about bot operation")

# Warning messages
logger.warning("Warning message for business logic issues")

# Error messages
logger.error("Error message for service failures")

# Critical errors
logger.critical("Critical error requiring immediate attention")
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
LOG_LEVEL=DEBUG poetry run python -m tgbot
```

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL is running
   - Verify connection parameters in `.env`
   - Check database exists and user has permissions

2. **Redis Connection Issues**
   - Check Redis is running
   - Verify Redis configuration
   - Check network connectivity

3. **OpenAI API Issues**
   - Verify API key is correct
   - Check API quota and billing
   - Verify network connectivity

## 🔧 Configuration

### Environment Variables

All configuration is managed through environment variables:

```bash
# Bot configuration
COMMON_BOT_TOKEN=your_bot_token
COMMON_ENCRYPTION_KEY=your_32_character_key
COMMON_ADMINS=123456789,987654321

# Database configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=mentorbot
POSTGRES_PASSWORD=password
POSTGRES_DB=mentorbot

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# OpenAI configuration
OPENAI_API_KEY=your_openai_api_key

# Payment configuration
PROVIDER_ENABLED=true
PROVIDER_TOKEN=your_provider_token
PROVIDER_CURRENCY=RUB
PROVIDER_PRICE=10000
```

### Configuration Classes

Configuration is managed through Pydantic models:

- `CommonConfig`: Bot settings
- `PostgresConfig`: Database settings
- `RedisConfig`: Redis settings
- `ProviderConfig`: Payment settings

## 📦 Dependencies

### Core Dependencies

- **aiogram**: Telegram bot framework
- **SQLAlchemy**: ORM for database operations
- **asyncpg**: PostgreSQL async driver
- **redis**: Redis client
- **pydantic**: Data validation and settings
- **openai**: OpenAI API client
- **qdrant-client**: Vector database client

### Development Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting
- **ruff**: Linting and formatting
- **mypy**: Type checking

## 🚀 Deployment

### Docker Deployment

```bash
# Build production image
docker build -t mentorbot .

# Run with docker-compose
docker-compose up -d

# Scale bot instances
docker-compose up -d --scale tgbot=3
```

### Systemd Service

```bash
# Install service file
sudo cp systemd/tgbot.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable tgbot
sudo systemctl start tgbot

# Check status
sudo systemctl status tgbot

# View logs
sudo journalctl -u tgbot -f
```

## 🤝 Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Update documentation if needed
7. Submit a pull request

### Commit Message Format

Use conventional commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
test: add tests
refactor: refactor code
style: formatting changes
```

### Code Review Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Error handling is appropriate
- [ ] Logging is added where needed

## 📚 Additional Resources

- [aiogram Documentation](https://docs.aiogram.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)