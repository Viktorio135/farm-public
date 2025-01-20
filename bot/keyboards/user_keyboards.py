from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="сдать скрин")],
        ],
        resize_keyboard=True
    )

def channels_keyboard(channels):
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{channel['name']}",
            callback_data=f"channel_{channel['id']}"
        )]
        for channel in channels
    ])

    return keyboard