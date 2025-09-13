# Развертывание MentorBot в k0s

Этот документ описывает различные способы развертывания MentorBot в кластере k0s.

## Предварительные требования

- k0s кластер (версия 1.28+)
- kubectl настроен для доступа к кластеру
- Docker для сборки образов
- GitHub Actions для CI/CD (опционально)

## Способы развертывания

### 1. Прямое развертывание с kubectl

#### Шаг 1: Подготовка секретов

```bash
# Скопируйте шаблон секретов
cp k8s/secrets-template.yaml k8s/secret.yaml

# Отредактируйте файл с реальными значениями
nano k8s/secret.yaml

# Или используйте скрипт для интерактивной настройки
chmod +x scripts/setup-secrets.sh
./scripts/setup-secrets.sh
```

#### Шаг 2: Настройка конфигурации

```bash
# Отредактируйте конфигурацию при необходимости
nano k8s/configmap.yaml
```

#### Шаг 3: Развертывание

```bash
# Для staging окружения
kubectl apply -k k8s/

# Для production окружения
kubectl apply -k k8s/production/
```

### 2. Развертывание с Helm

#### Шаг 1: Установка Helm

```bash
# Установите Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Шаг 2: Настройка values.yaml

```bash
# Отредактируйте конфигурацию
nano helm/mentor-bot/values.yaml
```

#### Шаг 3: Установка

```bash
# Добавьте репозиторий (если используете внешний)
helm repo add mentor-bot https://your-helm-repo.com

# Установите приложение
helm install mentor-bot ./helm/mentor-bot \
  --namespace mentor-bot \
  --create-namespace \
  --set secrets.common.botToken="your-bot-token" \
  --set secrets.common.encryptionKey="your-encryption-key" \
  --set secrets.postgres.password="your-postgres-password"
```

### 3. Развертывание с ArgoCD

#### Шаг 1: Установка ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Шаг 2: Создание приложения

```bash
# Для Kustomize
kubectl apply -f argocd/mentor-bot-app.yaml

# Для Helm
kubectl apply -f argocd/mentor-bot-helm-app.yaml
```

## CI/CD с GitHub Actions

### Настройка секретов в GitHub

Добавьте следующие секреты в настройках репозитория:

- `KUBE_CONFIG_STAGING` - kubeconfig для staging кластера
- `KUBE_CONFIG_PRODUCTION` - kubeconfig для production кластера
- `SLACK_WEBHOOK` - webhook для уведомлений (опционально)

### Workflow

GitHub Actions workflow автоматически:
1. Запускает тесты и линтинг
2. Собирает Docker образ
3. Пушит образ в GitHub Container Registry
4. Развертывает в staging (при push в develop)
5. Развертывает в production (при push в main)

## Мониторинг и логирование

### Просмотр логов

```bash
# Логи бота
kubectl logs -f deployment/mentor-bot -n mentor-bot

# Логи всех компонентов
kubectl logs -f -l app=mentor-bot -n mentor-bot
```

### Проверка статуса

```bash
# Статус подов
kubectl get pods -n mentor-bot

# Статус сервисов
kubectl get svc -n mentor-bot

# Описание подов
kubectl describe pods -n mentor-bot
```

### Масштабирование

```bash
# Увеличить количество реплик
kubectl scale deployment mentor-bot --replicas=3 -n mentor-bot

# Автомасштабирование (если настроено)
kubectl autoscale deployment mentor-bot --cpu-percent=70 --min=1 --max=10 -n mentor-bot
```

## Обновление приложения

### Обновление образа

```bash
# Обновить тег образа в манифестах
kubectl set image deployment/mentor-bot mentor-bot=ghcr.io/YOUR_USERNAME/mentor-bot:v1.1.0 -n mentor-bot

# Или через Kustomize
kubectl apply -k k8s/
```

### Откат

```bash
# Посмотреть историю развертываний
kubectl rollout history deployment/mentor-bot -n mentor-bot

# Откатиться к предыдущей версии
kubectl rollout undo deployment/mentor-bot -n mentor-bot

# Откатиться к конкретной версии
kubectl rollout undo deployment/mentor-bot --to-revision=2 -n mentor-bot
```

## Устранение неполадок

### Частые проблемы

1. **Поды не запускаются**
   ```bash
   kubectl describe pod <pod-name> -n mentor-bot
   kubectl logs <pod-name> -n mentor-bot
   ```

2. **Проблемы с секретами**
   ```bash
   kubectl get secrets -n mentor-bot
   kubectl describe secret mentor-bot-secrets -n mentor-bot
   ```

3. **Проблемы с подключением к БД**
   ```bash
   kubectl exec -it deployment/postgres -n mentor-bot -- psql -U mentorbot -d mentorbot
   ```

### Полезные команды

```bash
# Перезапустить развертывание
kubectl rollout restart deployment/mentor-bot -n mentor-bot

# Проверить события
kubectl get events -n mentor-bot --sort-by='.lastTimestamp'

# Проверить ресурсы
kubectl top pods -n mentor-bot
kubectl top nodes
```

## Безопасность

### Рекомендации

1. Используйте Sealed Secrets для хранения секретов
2. Настройте Network Policies для ограничения трафика
3. Используйте RBAC для ограничения доступа
4. Регулярно обновляйте образы и зависимости
5. Настройте мониторинг безопасности

### Sealed Secrets

```bash
# Установите kubeseal
wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/kubeseal-0.18.0-linux-amd64.tar.gz
tar xzf kubeseal-0.18.0-linux-amd64.tar.gz
sudo install -m 755 kubeseal /usr/local/bin/

# Получите публичный ключ
kubeseal --fetch-cert --controller-name=sealed-secrets-controller --controller-namespace=kube-system > public.pem

# Зашифруйте секреты
kubeseal --format=yaml --cert=public.pem < k8s/secret.yaml > k8s/sealed-secret.yaml
```