#!/bin/bash

# Скрипт для настройки секретов в Kubernetes
# Используйте этот скрипт для безопасной настройки секретов

set -e

NAMESPACE="mentor-bot"
SECRET_NAME="mentor-bot-secrets"

echo "🔐 Настройка секретов для MentorBot..."

# Проверяем, что kubectl доступен
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не найден. Установите kubectl и настройте доступ к кластеру."
    exit 1
fi

# Создаем namespace если не существует
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "📝 Введите значения для секретов:"

# Функция для безопасного ввода секретов
read_secret() {
    local prompt="$1"
    local var_name="$2"
    local is_json="$3"
    
    echo -n "$prompt: "
    read -s value
    echo
    
    if [ "$is_json" = "true" ]; then
        # Проверяем, что это валидный JSON
        echo "$value" | jq . > /dev/null 2>&1 || {
            echo "❌ Неверный JSON формат для $var_name"
            exit 1
        }
    fi
    
    # Кодируем в base64
    encoded_value=$(echo -n "$value" | base64 -w 0)
    echo "$var_name: $encoded_value"
}

# Создаем временный файл для секретов
TEMP_SECRET_FILE=$(mktemp)

cat > "$TEMP_SECRET_FILE" << EOF
apiVersion: v1
kind: Secret
metadata:
  name: $SECRET_NAME
  namespace: $NAMESPACE
type: Opaque
data:
EOF

# Собираем секреты
echo "🤖 Telegram Bot Token:"
read_secret "COMMON_BOT_TOKEN" "COMMON_BOT_TOKEN" "false" >> "$TEMP_SECRET_FILE"

echo "🔑 Encryption Key (32 символа):"
read_secret "COMMON_ENCRYPTION_KEY" "COMMON_ENCRYPTION_KEY" "false" >> "$TEMP_SECRET_FILE"

echo "👥 Admin IDs (JSON массив, например: [123456789, 987654321]):"
read_secret "COMMON_ADMINS" "COMMON_ADMINS" "true" >> "$TEMP_SECRET_FILE"

echo "🐘 PostgreSQL Password:"
read_secret "POSTGRES_PASSWORD" "POSTGRES_PASSWORD" "false" >> "$TEMP_SECRET_FILE"

echo "🔴 Redis Password:"
read_secret "REDIS_PASSWORD" "REDIS_PASSWORD" "false" >> "$TEMP_SECRET_FILE"

echo "💳 Provider Token:"
read_secret "PROVIDER_TOKEN" "PROVIDER_TOKEN" "false" >> "$TEMP_SECRET_FILE"

echo "🤖 OpenAI API Key:"
read_secret "OPENAI_API_KEY" "OPENAI_API_KEY" "false" >> "$TEMP_SECRET_FILE"

# Применяем секреты
echo "🚀 Применение секретов в кластер..."
kubectl apply -f "$TEMP_SECRET_FILE"

# Удаляем временный файл
rm "$TEMP_SECRET_FILE"

echo "✅ Секреты успешно настроены!"
echo "🔍 Проверка: kubectl get secrets -n $NAMESPACE"