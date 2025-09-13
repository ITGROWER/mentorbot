# Манифесты для k3s с секретами

Этот репозиторий содержит примеры Kubernetes манифестов для работы с секретами в k3s кластере.

## Обзор файлов

- `secrets-manifest.yaml` - Основные примеры различных типов секретов
- `configmap-with-secrets.yaml` - Пример совместного использования ConfigMap и Secret

## Типы секретов

### 1. Opaque Secret
Базовый тип секрета для произвольных данных:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  username: YWRtaW4=  # base64: admin
  password: cGFzc3dvcmQxMjM=  # base64: password123
```

### 2. Docker Registry Secret
Для аутентификации с приватными Docker registry:
```yaml
type: kubernetes.io/dockerconfigjson
```

### 3. TLS Secret
Для хранения SSL/TLS сертификатов:
```yaml
type: kubernetes.io/tls
data:
  tls.crt: <base64-certificate>
  tls.key: <base64-private-key>
```

### 4. SSH Auth Secret
Для SSH ключей:
```yaml
type: kubernetes.io/ssh-auth
data:
  ssh-privatekey: <base64-ssh-key>
```

### 5. Basic Auth Secret
Для HTTP Basic Authentication:
```yaml
type: kubernetes.io/basic-auth
data:
  username: <base64-username>
  password: <base64-password>
```

## Способы использования секретов

### 1. Переменные окружения
```yaml
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: app-secrets
      key: password
```

### 2. Загрузка всех ключей из ConfigMap/Secret
```yaml
envFrom:
- secretRef:
    name: app-secrets
- configMapRef:
    name: app-config
```

### 3. Монтирование как файлы
```yaml
volumeMounts:
- name: secret-volume
  mountPath: "/etc/secrets"
  readOnly: true

volumes:
- name: secret-volume
  secret:
    secretName: app-secrets
    defaultMode: 0600
```

### 4. ImagePullSecrets
```yaml
spec:
  imagePullSecrets:
  - name: docker-registry-secret
```

## Команды для работы с секретами

### Создание секрета из командной строки
```bash
# Создание секрета с данными
kubectl create secret generic app-secrets \
  --from-literal=username=admin \
  --from-literal=password=password123

# Создание Docker registry секрета
kubectl create secret docker-registry docker-registry-secret \
  --docker-server=registry.example.com \
  --docker-username=username \
  --docker-password=password

# Создание TLS секрета
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

### Кодирование данных в base64
```bash
# Кодирование строки
echo -n "password123" | base64

# Декодирование
echo "cGFzc3dvcmQxMjM=" | base64 -d
```

### Просмотр секретов
```bash
# Список всех секретов
kubectl get secrets

# Подробная информация о секрете
kubectl describe secret app-secrets

# Получение значения из секрета (декодированное)
kubectl get secret app-secrets -o jsonpath="{.data.password}" | base64 -d
```

## Развертывание в k3s

### 1. Применение манифестов
```bash
# Применить основные секреты
kubectl apply -f secrets-manifest.yaml

# Применить пример с ConfigMap
kubectl apply -f configmap-with-secrets.yaml
```

### 2. Проверка статуса
```bash
# Проверить поды
kubectl get pods

# Проверить логи
kubectl logs -l app=app-with-secrets

# Проверить переменные окружения в поде
kubectl exec -it <pod-name> -- env | grep DB_

# Проверить смонтированные файлы
kubectl exec -it <pod-name> -- ls -la /etc/secrets/
```

## Безопасность

### Лучшие практики:
1. **Никогда не коммитьте секреты в Git** - используйте tools как Sealed Secrets или External Secrets
2. **Используйте RBAC** для ограничения доступа к секретам
3. **Регулярно ротируйте** секреты
4. **Используйте минимальные права** для сервисных аккаунтов
5. **Мониторьте доступ** к секретам

### Настройка RBAC для секретов:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader-binding
subjects:
- kind: ServiceAccount
  name: app-service-account
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

## Troubleshooting

### Частые проблемы:

1. **Secret не найден**
   ```bash
   kubectl get secrets -n <namespace>
   ```

2. **Неправильное кодирование base64**
   ```bash
   echo -n "your-string" | base64
   ```

3. **Проблемы с правами доступа к файлам**
   ```yaml
   defaultMode: 0600  # или нужные права
   ```

4. **ImagePullBackOff с Docker registry**
   ```bash
   kubectl describe pod <pod-name>
   # Проверить imagePullSecrets
   ```

### Дебаггинг:
```bash
# Проверить события
kubectl get events --sort-by=.metadata.creationTimestamp

# Детальная информация о поде
kubectl describe pod <pod-name>

# Логи контейнера
kubectl logs <pod-name> -c <container-name>
```

## Дополнительные инструменты

### Sealed Secrets
Для шифрования секретов в Git:
```bash
# Установка
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# Создание sealed secret
kubeseal -f secret.yaml -w sealedsecret.yaml
```

### External Secrets Operator
Для интеграции с внешними системами управления секретами (Vault, AWS Secrets Manager):
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace
```