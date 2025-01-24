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
from keyboards.user_keyboards import cancel_keyboard, main_menu_keyboard, channels_keyboard
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

                        print(message)

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
        groups = await get_channels()
        in_channels = False
        for Groups in groups:
            members = await get_chat_members(int(Groups['chat_id']))
            if str(message.from_user.id) in members:
                in_channels = True
                break
        if in_channels:
            avatar = await bot.get_user_profile_photos(message.from_user.id)
            avatar = avatar.total_count > 0
            await create_user(message.from_user.id, message.from_user.username, avatar)
            await message.answer(
"""Добро пожаловать!

Скорее заходи в задания и зарабатывай деньги!
        """
                , reply_markup=main_menu_keyboard())
    else:
        await message.answer(
"""Добро пожаловать!

Скорее заходи в задания и зарабатывай деньги!
"""
        , reply_markup=main_menu_keyboard())



@router.message(F.text.lower() == "отмена", TaskStates.SCREENSHOT)
async def cancel_screenshot_upload(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Отправляем сообщение с главным меню
    await message.answer(
        "Загрузка скриншота отменена.",
        reply_markup=main_menu_keyboard()
    )



@router.message(F.text == "сдать скрин")
async def show_tasks(message: Message, bot: Bot):
    tasks = await get_tasks(message.from_user.id)
    groups = tasks['groups']
    tasks = tasks["tasks"]
    
    if tasks and groups:
        user_permisions = []
        for group in groups:
            chat_member = await bot.get_chat_member(group['chat_id'], message.from_user.id)
            if chat_member and chat_member.status != 'left' and chat_member.status != 'kicked':
                user_permisions.append(group)
        if user_permisions:
            avalible_channels = []
            for group in user_permisions:
                for task in tasks:
                    for gr_task in task['groups']:
                        if int(group['chat_id']) == int(gr_task['chat_id']):
                                flag = True
                                for i in avalible_channels:
                                    if i['channel'] == task['channel']['name']:
                                        flag = False
                                        break
                                if flag:
                                    avalible_channels.append({
                                        'channel': task['channel']['name'], 
                                        'id': task['id'],
                                        'group': group['id']
                                    })
                            
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
    group_id = int(callback.data.split("_")[2])
    task_data = await get_tasks(callback.from_user.id)
    task_name = None
    for task in task_data['tasks']:
        if task['id'] == task_id:
            task_name = task['name']
            break
    await callback.message.answer(f"Задание '{task_name}' #{task_id}\n\nПрикрепите скриншот подтверждения:", reply_markup=cancel_keyboard())
    await state.set_state(TaskStates.SCREENSHOT)  # Устанавливаем состояние
    await state.update_data(task_id=task_id)
    await state.update_data(group_id=group_id)



@router.message(F.photo, TaskStates.SCREENSHOT)  # Используем State как фильтр
async def process_screenshot(message: Message, state: FSMContext, bot: Bot):

    # Получаем данные из состояния
    data = await state.get_data()
    task_id = data.get("task_id")
    group_id = data.get("group_id")

    # Извлекаем file_id самого большого размера изображения
    photo = message.photo[-1]  # Берем последний элемент (самое большое изображение)
    file_id = photo.file_id

    # Скачиваем изображение
    file = await bot.get_file(file_id)
    file_path = file.file_path
    image_url = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
    
    # Отправляем изображение в Django API
    if await send_confirmation(image_url, message.from_user.id, task_id, group_id):
        await message.answer(
            'Отчет отправлен, ожидайте результата!',
            reply_markup=main_menu_keyboard()
        )
    else:
        await message.answer(
            'Что-то пошло не так, уже чиним(',
            reply_markup=main_menu_keyboard()
        )

    # Очищаем состояние
    await state.clear()