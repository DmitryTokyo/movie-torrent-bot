from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.constants import PAGINATION_STEP


def build_results_navigation_keyboard_without_pagination() -> InlineKeyboardMarkup:
    keyboard = build_finish_search_keyboard()
    return InlineKeyboardMarkup([keyboard])


def build_finish_search_keyboard() -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton('🔄 Хочу другой', callback_data='another'),
        InlineKeyboardButton('✅ Закончили', callback_data='done'),
    ]



def build_results_navigation_keyboard_with_pagination(
    pagination_start_range: int,
    pagination_end_range: int,
    total_results: int,
) -> InlineKeyboardMarkup:
    if pagination_start_range == 0:
        keyboard = [
            [InlineKeyboardButton('➡️ Вперёд', callback_data=f'next_{pagination_end_range}')],
            build_finish_search_keyboard()
        ]
        return InlineKeyboardMarkup(keyboard)
    if total_results - pagination_end_range <= PAGINATION_STEP:
        keyboard = [
            [
                InlineKeyboardButton('⏮️ В начало', callback_data='in_start'),
                InlineKeyboardButton('⬅️ Назад', callback_data=f'prev_{pagination_start_range}'),
            ],
            build_finish_search_keyboard()
        ]
        return InlineKeyboardMarkup(keyboard)

    keyboard = [
        [
            InlineKeyboardButton('⏮️ В начало', callback_data='in_start'),
            InlineKeyboardButton('⬅️ Назад', callback_data=f'prev_{pagination_start_range}'),
            InlineKeyboardButton('➡️ Вперёд', callback_data=f'next_{pagination_end_range}'),
        ],
        build_finish_search_keyboard()
    ]
    return InlineKeyboardMarkup(keyboard)


def build_download_movie_keyboard()-> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📥 Скачиваем?", callback_data='download')],
        build_finish_search_keyboard()
    ]
    return InlineKeyboardMarkup(keyboard)