# LMS Backend API

Backend-сервер для платформы онлайн-обучения (Learning Management System). Реализует CRUD-операции для курсов, уроков и
пользователей. Построен на **Django** + **Django REST Framework**. Возвращает данные в формате JSON.

## Быстрый старт с Docker

### Клонировать репозиторий

```bash
git clone git@github.com:mossssolma-ui/drf.git
```

### Создать файл .env

```bash
# ===== DJANGO =====
SECRET_KEY=
DEBUG=

# ===== POSTGRESQL (для Django и контейнера) =====
POSTGRES_ENGINE=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

# ===== STRIPE =====
STRIPE_API_KEY=

# ===== EMAIL =====
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# ===== REDIS =====
REDIS_HOST=
REDIS_PORT=
REDIS_DB=

# ===== SUPERUSER (для автоматического создания суперюзера) =====
CSU_EMAIL=
CSU_PASSWORD=
```

### Запустить проект

```bash
docker-compose up -d --build
```
После сборки, автоматически создадутся суперпользователь (CSU_EMAIL) и платежи (create_payments)

### Посмотреть статус контейнеров

```bash
docker-compose ps
```
Пример результата
```
time="2026-07-04T13:29:48+03:00" level=warning msg="D:\\Programming\\SKYPRO\\drf\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
NAME           IMAGE           COMMAND                  SERVICE   CREATED          STATUS                    PORTS
drf-celery-1   drf-celery      "celery -A config wo…"   celery    45 seconds ago   Up 12 seconds             8000/tcp
drf-db-1       postgres:16.0   "docker-entrypoint.s…"   db        46 seconds ago   Up 43 seconds (healthy)   5432/tcp
drf-lms-1      drf-lms         "bash -c 'python man…"   lms       45 seconds ago   Up 12 seconds             0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
drf-redis-1    redis:alpine    "docker-entrypoint.s…"   redis     46 seconds ago   Up 43 seconds (healthy)   6379/tcp
```

### Проверить работу приложения
```bash
http://localhost:8000
```
Доступ к админке
```bash
http://localhost:8000/admin
```