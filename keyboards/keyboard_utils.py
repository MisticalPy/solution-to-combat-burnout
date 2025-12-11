from lexicon.lexicon_ru import RU

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Создаем объекты инлайн-кнопок
button_1 = InlineKeyboardButton(text=RU["start_dialog"],
                                callback_data="start_dialog")
# Создаем объекты инлайн-кнопок
button_help = InlineKeyboardButton(text=RU["help_button"],
                                   callback_data="help_button")

# Создаем объекты инлайн-кнопок
button_answer_yes = InlineKeyboardButton(text="Да", callback_data="yes")

# Создаем объекты инлайн-кнопок
button_answer_no = InlineKeyboardButton(text="Нет", callback_data="No")

# Создаем объект инлайн-клавиатуры
keyboard_start_dialog = InlineKeyboardMarkup(inline_keyboard=[[button_1]])

# Создаем объект инлайн-клавиатуры
keyboard_help_dialog = InlineKeyboardMarkup(inline_keyboard=[[button_help]])

# Создаем объект инлайн-клавиатуры
keyboard_answer = InlineKeyboardMarkup(
    inline_keyboard=[[button_answer_yes, button_answer_no]])
