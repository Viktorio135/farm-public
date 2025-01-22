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
            callback_data=f"channel_{group['id']}"
        )]
        for group in groups
    ])

    return keyboard