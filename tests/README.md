# MentorBot Test Suite

This directory contains comprehensive tests for the MentorBot Telegram bot application.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── fixtures/                # Test data fixtures
│   └── sample_data.py      # Sample data for testing
├── unit/                   # Unit tests
│   ├── test_models.py      # Database model tests
│   ├── test_repositories.py # Repository tests
│   ├── test_handlers.py    # Handler tests
│   └── test_services.py    # Service tests
├── integration/            # Integration tests
│   └── test_bot_workflow.py # End-to-end workflow tests
├── utils.py                # Test utilities and helpers
└── README.md              # This file
```

## Running Tests

### Prerequisites

Install test dependencies:
```bash
poetry install --with dev
```

### Run All Tests
```bash
poetry run pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
poetry run pytest tests/unit/

# Integration tests only
poetry run pytest tests/integration/

# Tests with specific markers
poetry run pytest -m unit
poetry run pytest -m integration
```

### Run Tests with Coverage
```bash
poetry run pytest --cov=tgbot --cov-report=html --cov-report=term-missing
```

### Run Tests in Verbose Mode
```bash
poetry run pytest -v
```

## Test Categories

### Unit Tests (`tests/unit/`)

- **test_models.py**: Tests for database models (User, Mentor, Conversation)
- **test_repositories.py**: Tests for repository CRUD operations
- **test_handlers.py**: Tests for bot message handlers
- **test_services.py**: Tests for AI services, encryption, and utilities

### Integration Tests (`tests/integration/`)

- **test_bot_workflow.py**: End-to-end tests for complete user journeys

## Test Fixtures

### Database Fixtures
- `test_engine`: In-memory SQLite database for testing
- `test_session`: Database session for tests
- `test_repository`: Repository instance with test session

### Bot Fixtures
- `test_bot`: Mock Telegram bot instance
- `test_dispatcher`: Bot dispatcher with memory storage
- `test_config`: Test configuration with safe defaults

### Mock Fixtures
- `mock_openai_service`: Mock OpenAI API responses
- `mock_qdrant_service`: Mock Qdrant vector database operations
- `sample_user_data`: Sample user data for testing
- `sample_mentor_data`: Sample mentor data for testing

## Writing Tests

### Unit Test Example
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

### Integration Test Example
```python
@pytest.mark.asyncio
async def test_complete_user_registration_flow(test_repository: Repository):
    """Test complete registration flow for a new user."""
    # Test the entire flow from /start to mentor creation
    pass
```

## Test Utilities

### MockTelegramObjects
Factory for creating mock Telegram objects:
```python
user = MockTelegramObjects.create_user(user_id=123456789)
message = MockTelegramObjects.create_message(text="Hello!")
```

### DatabaseTestHelpers
Helper functions for database testing:
```python
user = await DatabaseTestHelpers.create_test_user(session)
mentor = await DatabaseTestHelpers.create_test_mentor(session, user.id)
```

### MockAIServices
Mock AI services for testing:
```python
with MockAIServices.patch_openai_services():
    # Test code that uses OpenAI services
    pass
```

## Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures** for common setup and teardown
4. **Mock external services** to avoid dependencies
5. **Test both success and failure cases**
6. **Use async/await properly** for async tests
7. **Clean up test data** after each test
8. **Use meaningful assertions** with descriptive error messages

## Continuous Integration

Tests are designed to run in CI/CD pipelines with:
- No external dependencies (mocked services)
- Fast execution (in-memory database)
- Deterministic results (no random data)
- Clear error reporting

## Debugging Tests

### Run Single Test
```bash
poetry run pytest tests/unit/test_models.py::TestDBUser::test_user_creation -v
```

### Run with Debug Output
```bash
poetry run pytest -s -v --tb=long
```

### Run with Logging
```bash
poetry run pytest --log-cli-level=DEBUG
```

## Coverage

The test suite aims for high code coverage:
- Unit tests: >90% coverage for individual components
- Integration tests: Cover all major user workflows
- Service tests: Cover all external service interactions

View coverage report:
```bash
poetry run pytest --cov=tgbot --cov-report=html
open htmlcov/index.html
```