import websockets
import asyncio
import json

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup


from services.task_service import get_tasks, create_user_task, send_confirmation, get_channels
from services.user_service import get_user, create_user
from keyboards.user_keyboards import main_menu_keyboard, channels_keyboard
from utils.get_members import get_chat_members

router = Router()


async def listen_to_websocket(bot: Bot):
    uri = "ws://127.0.0.1:8000/ws/notifications/"

    while True:  # Бесконечный цикл для переподключения
        try:
            async with websockets.connect(uri) as websocket:
                print("Бот подключился к WebSocket")
                while True:
                    try:
                        # Ожидаем сообщение от бэкенда
                        message = await websocket.recv()

                        # Преобразуем сообщение в словарь
                        data = json.loads(message)

                        # Извлекаем JSON-строку из ключа 'message'
                        data = data['message']

                        # Теперь parsed_data — это словарь с данными
                        if 'action' in data:
                            data = json.loads(data)
                            if data['action'] == 'get_channel_members_count':
                                members = await get_channel_members_count(int(data['channel_id']), bot)
                                await websocket.send(json.dumps({
                                    'action': 'channel_members_count',
                                    'members_count': str(members),
                                }))
                        else:
                            chat_id = data['chat_id']
                            text = data['text']

                            # Отправляем уведомление пользователю
                            await bot.send_message(chat_id=chat_id, text=text)
                    except websockets.ConnectionClosed as e:
                        print(f"Соединение закрыто: {e}")
                        break  # Выходим из внутреннего цикла и пытаемся переподключиться
                    except Exception as e:
                        print(f"Ошибка: {e}")
                        break  # Выходим из внутреннего цикла и пытаемся переподключиться

        except Exception as e:
            print(f"Ошибка подключения к WebSocket: {e}")
            print("Повторная попытка подключения через 5 секунд...")
            await asyncio.sleep(5)  # Ждем 5 секунд перед повторной попыткой


async def get_channel_members_count(channel_id: str, bot: Bot) -> int:
    """
    Получает количество пользователей в канале.
    """
    try:
        # Используем метод get_chat_member_count для получения количества участников
        members = await get_chat_members(channel_id)
        return members
    except Exception as e:
        print(f"Ошибка при получении количества пользователей в канале: {e}")
        return 0  # В случае ошибки возвращаем 0



# Определяем состояния
class TaskStates(StatesGroup):
    SCREENSHOT = State()

@router.message(Command("start"))
async def start(message: Message, bot: Bot):
    user = await get_user(message.from_user.id)
    if not user:
        channels = await get_channels()
        in_channels = False
        for channel in channels:
            members = await get_chat_members(int(channel['chat_id']))
            if str(message.from_user.id) in members:
                in_channels = True
                break
        if in_channels:
            avatar = await bot.get_user_profile_photos(message.from_user.id)
            avatar = avatar.total_count > 0
            print(avatar)
            await create_user(message.from_user.id, message.from_user.username, avatar)
            await message.answer(
"""Добро пожаловать!

На нашу площадку ххх

Скорее заходи в задания и зарабатывай деньги!
        """
                , reply_markup=main_menu_keyboard())
    else:
        await message.answer(
"""Добро пожаловать!

На нашу площадку ххх

Скорее заходи в задания и зарабатывай деньги!
"""
        , reply_markup=main_menu_keyboard())

@router.message(F.text == "Баланс")
async def show_balance(message: Message):
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(f"Ваш баланс: {user['balance']} руб.")
    else:
        await message.answer("Пользователь не найден.")

@router.message(F.text == "Задания")
async def show_tasks(message: Message, bot: Bot):
    tasks = await get_tasks(message.from_user.id)
    channels = tasks['channels']
    tasks = tasks["tasks"]
    
    if tasks and channels:
        user_permisions = []
        for channel in channels:
            chat_member = await bot.get_chat_member(channel['chat_id'], message.from_user.id)


            if chat_member:
                user_permisions.append(channel)
        if user_permisions:
            avalible_channels = []
            for channel in user_permisions:
                for task in tasks:
                    if int(channel['id']) == int(task['channels']):
                        avalible_channels.append(channel)
            if avalible_channels:            
                await message.answer(
                    "Список доступных каналов:",
                    reply_markup=channels_keyboard(avalible_channels)
                )
            else:
                await message.answer(
                    'К сожалению сейчас нет доступных каналов'
                )
        else:
            await message.answer(
                'Вы не состоите ни в одном канале('
            )
    else:
        await message.answer("Нет доступных каналов.")

@router.callback_query(F.data.startswith("channel_"))
async def complete_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    await create_user_task(callback.from_user.id, task_id)
    await callback.message.answer("Прикрепите скриншот подтверждения:")
    await state.set_state(TaskStates.SCREENSHOT)  # Устанавливаем состояние
    await state.update_data(task_id=task_id)



@router.message(F.photo, TaskStates.SCREENSHOT)  # Используем State как фильтр
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):

    # Получаем данные из состояния
    data = await state.get_data()
    task_id = data.get("task_id")

    # Извлекаем file_id самого большого размера изображения
    photo = message.photo[-1]  # Берем последний элемент (самое большое изображение)
    file_id = photo.file_id

    # Скачиваем изображение
    file = await bot.get_file(file_id)
    file_path = file.file_path
    image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    
    # Отправляем изображение в Django API
    if await send_confirmation(image_url, message.from_user.id, task_id):
        await message.answer(
            'Отчет отправлен, ожидайте результата!',
        )
    else:
        await message.answer(
            'Что-то пошло не так, уже чиним('
        )

    # Очищаем состояние
    await state.clear()