from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="сдать скрин")],
        ],
        resize_keyboard=True
    )

def channels_keyboard(groups):
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{group['channel']}",
            callback_data=f"channel_{group['id']}_{group['group']}"
        )]
        for group in groups
    ])

    return keyboard


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='отмена')]
        ],
        resize_keyboard=True
    )