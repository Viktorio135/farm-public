from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Баланс")],
            [KeyboardButton(text="Задания")],
            [KeyboardButton(text="История выполнений")]
        ],
        resize_keyboard=True
    )

def tasks_keyboard(tasks):
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{task['channel_name']} ({task['reward']} руб.)",
            callback_data=f"task_{task['id']}"
        )]
        for task in tasks
    ])

    return keyboard