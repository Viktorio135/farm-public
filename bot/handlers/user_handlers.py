from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from services.task_service import get_tasks, create_user_task
from services.user_service import get_user, create_user
from keyboards.user_keyboards import main_menu_keyboard, tasks_keyboard

router = Router()

# Определяем состояния
class TaskStates(StatesGroup):
    SCREENSHOT = State()  # Используем State вместо строки

@router.message(Command("start"))
async def start(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await create_user(message.from_user.id, message.from_user.username)
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
async def show_tasks(message: Message):
    tasks = await get_tasks(message.from_user.id)
    if tasks:
        await message.answer(
            "Список заданий:",
            reply_markup=tasks_keyboard(tasks)
        )
    else:
        await message.answer("Нет доступных заданий.")

@router.callback_query(F.data.startswith("task_"))
async def complete_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[1])
    await create_user_task(callback.from_user.id, task_id)
    await callback.message.answer("Прикрепите скриншот подтверждения:")
    await state.set_state(TaskStates.SCREENSHOT)  # Устанавливаем состояние
    await state.update_data(task_id=task_id)

@router.message(F.photo, TaskStates.SCREENSHOT)  # Используем State как фильтр
async def process_screenshot(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get("task_id")
    # Сохраняем скриншот (здесь можно отправить его в Django API)
    await message.answer("Скриншот принят на рассмотрение.")
    await state.clear()