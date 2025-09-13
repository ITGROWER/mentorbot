# Kubernetes Manifests for MentorBot

Этот каталог содержит Kubernetes манифесты для развертывания MentorBot в кластере k0s.

## Структура файлов

- `namespace.yaml` - Namespace для приложения
- `configmap.yaml` - Конфигурация приложения
- `secret.yaml` - Шаблон для секретов
- `secrets-template.yaml` - Шаблон для заполнения секретов
- `postgres.yaml` - PostgreSQL база данных
- `redis.yaml` - Redis кэш
- `qdrant.yaml` - Qdrant векторная база данных
- `bot.yaml` - Основное приложение бота
- `kustomization.yaml` - Kustomize конфигурация
- `production/` - Конфигурация для production окружения

## Установка

### 1. Подготовка секретов

Скопируйте `secrets-template.yaml` в `secret.yaml` и заполните реальными значениями:

```bash
cp k8s/secrets-template.yaml k8s/secret.yaml
# Отредактируйте k8s/secret.yaml с реальными значениями
```

### 2. Обновление конфигурации

Отредактируйте `k8s/configmap.yaml` для настройки параметров приложения.

### 3. Развертывание

Для staging окружения:
```bash
kubectl apply -k k8s/
```

Для production окружения:
```bash
kubectl apply -k k8s/production/
```

### 4. Проверка статуса

```bash
kubectl get pods -n mentor-bot
kubectl logs -f deployment/mentor-bot -n mentor-bot
```

## Переменные окружения

### Обязательные секреты:
- `COMMON_BOT_TOKEN` - Токен Telegram бота
- `COMMON_ENCRYPTION_KEY` - Ключ шифрования
- `COMMON_ADMINS` - JSON массив с ID администраторов
- `POSTGRES_PASSWORD` - Пароль PostgreSQL
- `REDIS_PASSWORD` - Пароль Redis
- `PROVIDER_TOKEN` - Токен платежного провайдера
- `OPENAI_API_KEY` - API ключ OpenAI

### Конфигурация:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` - Настройки БД
- `REDIS_HOST`, `REDIS_PORT` - Настройки Redis
- `PROVIDER_CURRENCY`, `PROVIDER_PRICE`, `PROVIDER_MENTOR_PRICE` - Настройки платежей

## Масштабирование

Для production окружения используется конфигурация с 2 репликами и увеличенными ресурсами.

## Мониторинг

Приложение включает health checks для проверки работоспособности через Telegram API.