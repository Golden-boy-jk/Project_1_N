# NewsPortal

Учебный новостной портал на Django (+ DRF, Celery, Allauth, i18n).

## ✨ Возможности
- Публикации: новости и статьи, категории и подписки
- Аутентификация через Django Allauth (есть соц-провайдеры при желании)
- REST API на DRF (версирование `api/v1`)
- Уведомления на email, плановые рассылки через Celery Beat
- Локализация и часовые пояса пользователей
- Кэширование списков (опционально Redis)

---

## 🚀 Быстрый старт (локально)

### 1) Зависимости
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Переменные окружения
Создайте `.env` в корне проекта (рядом с `manage.py`) по образцу ниже:

```dotenv
# --- Base ---
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

# --- Database ---
# SQLite (по умолчанию в settings, можно оставить так для локалки)
# Для PostgreSQL используйте переменные ниже:
# DATABASE_URL=postgres://USER:PASSWORD@localhost:5432/newsportal

# --- Cache / Celery ---
REDIS_URL=redis://localhost:6379/0

# --- Email ---
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# Для боевого SMTP:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.example.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=...
# EMAIL_HOST_PASSWORD=...

# --- Locale ---
TIME_ZONE=Europe/Moscow
LANGUAGE_CODE=ru
```

> **Важно:** секреты (ключи, пароли) не коммитим в Git. `.env` попадает в `.gitignore`.

### 3) Миграции и суперпользователь
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4) Запуск сервера
```bash
python manage.py runserver
```

Сайт откроется на `http://127.0.0.1:8000/`.

---

## 🔌 Запуск Celery

В отдельных терминалах (с активированным виртуальным окружением):

### Worker
```bash
celery -A NewsPortal worker -l info
```

### Beat (периодические задачи)
```bash
celery -A NewsPortal beat -l info
```

> Для Redis нужен локально запущенный Redis (`redis-server`). В `.env` проверьте `REDIS_URL`.

---

## 🧭 Полезные маршруты

- Веб-часть: `http://127.0.0.1:8000/`
- Админка: `/admin/`
- API (пример): `/api/v1/news/`, `/api/v1/articles/`
- Документация API (если подключён drf-spectacular):
  - `/api/schema/` (OpenAPI)
  - `/api/docs/` (Swagger UI)

---

## 🛠 Разработка и качество кода

Рекомендуемые инструменты:
- Линтеры и форматтеры: `ruff`, `black`, `isort`
- Тесты: `pytest`, `pytest-django`

Пример установки:
```bash
pip install ruff black isort pytest pytest-django
```

Запуск линтеров:
```bash
ruff check .
black .
isort .
```

---

## 📦 Что ещё можно добавить позже
- Dockerfile и docker-compose (web + postgres + redis + celery + beat)
- pre-commit с ruff/black/isort
- Sentry/логирование
- Whitenoise или CDN для статики в проде
- Полные e2e тесты API