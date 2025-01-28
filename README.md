# Система распределенной накрутки подписчиков в Telegram

## Описание проекта

Основная задача — контроль выполнения заданий пользователями. После того как пользователь выполняет задание (например, подписывается на канал или группу), он отправляет скриншот с подтверждением в backend для проверки. 

В административной панели доступна детальная статистика по группам, каналам и пользователям. Также предусмотрено ручное редактирование данных пользователей: зачисление выполненных заданий, начисление баланса и другие операции.

---

## Техническая реализация

### Backend
Backend часть проекта реализована на **Django** и разделена на две основные части:
1. **Административная панель** — для управления данными и просмотра статистики.
2. **API** — для взаимодействия с frontend и Telegram-ботом.

Для связи с frontend используется **WebSocket** (библиотека Channels) и стандартные API-запросы. WebSocket необходим для двустороннего обмена данными, например, для отправки уведомлений пользователям и получения данных от Telegram.

### Telegram-бот
Пользовательская часть системы вынесена в Telegram-бота, написанного на **Aiogram 3**. Бот обеспечивает быстрый доступ к основному функционалу и взаимодействует с backend через WebSocket и API-запросы.

### Асинхронность и задачи
Для обеспечения высокой производительности весь код, где это возможно, реализован асинхронно. В качестве асинхронного драйвера для PostgreSQL используется **asyncpg**.

Для выполнения периодических и фоновых задач (например, CRON-задачи) используется **Celery** с хранилищем **Redis**.

---

## Административная панель

Административная часть выделена в отдельное приложение **Panel**. В нем описаны все модели базы данных. Frontend для админ-панели реализован на **HTML**, **CSS** и **JavaScript** с использованием шаблонизатора Django.

Доступ в админ-панель осуществляется через стандартный механизм **Django-администрирования**. Добавление новых администраторов выполняется вручную.

---

## API

API вынесен в отдельное приложение **API**. В нем реализовано взаимодействие между Telegram-ботом и backend. Основные функции:
- Обработка данных от пользователей.
- Отправка уведомлений через WebSocket.
- Взаимодействие с административной панелью.

---

## Telegram-бот на Aiogram

Бот написан с использованием **Aiogram 3** и является полностью асинхронным. Для удобства разработки и поддержки код разделен на модули:
- **Handlers** — обработчики команд и сообщений.
- **Keyboards** — клавиатуры и inline-кнопки.
- **Utils** — вспомогательные функции.
- **Services** — функции для взаимодействия с API.

---

## Установка и запуск

### Требования
Для запуска проекта необходимо установить следующие компоненты:
- Python 3.9 или выше
- PostgreSQL
- Redis
- Nginx
- Daphne
