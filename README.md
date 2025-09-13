# Манифесты k3s с секретами

Этот репозиторий содержит примеры манифестов Kubernetes для работы с секретами в k3s.

## Файлы

- `secret-examples.yaml` - базовые примеры создания и использования секретов
- `secret-best-practices.yaml` - продвинутые примеры с лучшими практиками безопасности

## Типы секретов

### 1. Opaque секреты
Самый распространенный тип секретов для хранения произвольных данных:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: cGFzc3dvcmQ=
```

### 2. TLS секреты
Для хранения сертификатов и ключей:
```yaml
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

### 3. Docker registry секреты
Для аутентификации в Docker registry:
```yaml
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-docker-config>
```

## Способы использования секретов

### Переменные окружения
```yaml
env:
- name: PASSWORD
  valueFrom:
    secretKeyRef:
      name: my-secret
      key: password
```

### Файлы через volume
```yaml
volumeMounts:
- name: secret-volume
  mountPath: /etc/secrets
volumes:
- name: secret-volume
  secret:
    secretName: my-secret
```

## Команды для работы с секретами

### Создание секрета из командной строки
```bash
# Создание секрета из литералов
kubectl create secret generic my-secret \
  --from-literal=username=admin \
  --from-literal=password=password

# Создание секрета из файлов
kubectl create secret generic my-secret \
  --from-file=username.txt \
  --from-file=password.txt

# Создание TLS секрета
kubectl create secret tls tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/key.key

# Создание Docker registry секрета
kubectl create secret docker-registry registry-secret \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password \
  --docker-email=user@example.com
```

### Кодирование в base64
```bash
echo -n 'admin' | base64
echo -n 'password' | base64
```

### Применение манифестов
```bash
# Применить базовые примеры
kubectl apply -f secret-examples.yaml

# Применить продвинутые примеры
kubectl apply -f secret-best-practices.yaml
```

### Просмотр секретов
```bash
# Список секретов
kubectl get secrets

# Подробная информация о секрете
kubectl describe secret my-secret

# Получить значение секрета (декодированное)
kubectl get secret my-secret -o jsonpath="{.data.username}" | base64 --decode
```

## Лучшие практики

1. **Используйте namespaces** для изоляции секретов
2. **Настройте RBAC** для ограничения доступа к секретам
3. **Используйте ServiceAccount** для подов, которые работают с секретами
4. **Не включайте секреты в Docker образы**
5. **Ротируйте секреты регулярно**
6. **Используйте внешние системы управления секретами** (HashiCorp Vault, AWS Secrets Manager)

## Безопасность

- Секреты хранятся в etcd в base64 кодировке (не зашифрованы!)
- Для k3s рекомендуется включить шифрование etcd:
```bash
k3s server --secrets-encryption
```

- Ограничьте доступ к API серверу
- Используйте Network Policies для ограничения сетевого доступа
- Регулярно аудируйте доступ к секретам

## Примеры использования

### Веб-приложение с базой данных
```yaml
# Секрет с данными для подключения к БД
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: <base64-encoded-user>
  password: <base64-encoded-password>
  host: <base64-encoded-host>

---
# Deployment приложения
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-web-app:latest
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
```

### HTTPS сервис с TLS
```yaml
apiVersion: v1
kind: Service
metadata:
  name: secure-service
spec:
  type: LoadBalancer
  ports:
  - port: 443
    targetPort: 8080
  selector:
    app: secure-app

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: secure-service
            port:
              number: 443
```

## Мониторинг и отладка

```bash
# Проверить, используется ли секрет
kubectl get pods -o yaml | grep -A 10 -B 10 secretKeyRef

# Проверить монтирование секретов
kubectl exec -it <pod-name> -- ls -la /etc/secrets/

# Логи подов с проблемами доступа к секретам
kubectl logs <pod-name> | grep -i secret
```