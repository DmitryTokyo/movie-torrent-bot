import os
from warnings import filterwarnings

from telegram import (
    BotCommand, Update, ReplyKeyboardRemove
)
from telegram.ext import (
    ContextTypes, CommandHandler, Application, ConversationHandler, MessageHandler, filters, CallbackQueryHandler,
)
from telegram.warnings import PTBUserWarning

from bot.constants import MAX_MOVIES_ON_MESSAGE, PAGINATION_STEP
from bot.keyboards import build_results_navigation_keyboard_without_pagination, \
    build_results_navigation_keyboard_with_pagination, build_download_movie_keyboard
from bot.messages import get_search_results_movies_message, get_search_result_movies_message
from movies_search import get_searching_result, download_movie

MOVIE_NAME, SEARCH_RESULT = range(2)
filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


async def movie_name_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            'Введи название кино, которое хочешь найти',
            reply_markup=None,
        )
    elif update.callback_query:
        await update.callback_query.answer()
        chat_id = update.callback_query.message.chat_id
        await context.bot.send_message(
            chat_id=chat_id,
            text='Введи название кино, которое хочешь найти',
        )
    return MOVIE_NAME


async def movies_link_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_name = update.message.text
    loading_message = await update.message.reply_text('Ищу фильм... Подождите ⏳')
    search_results = get_searching_result(movie_name)
    if search_results:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=loading_message.message_id,
        )
        if len(search_results) <= MAX_MOVIES_ON_MESSAGE:
            return await show_movies_without_pagination(update, context, search_results)

        return await show_movies_with_pagination(update, context, search_results)

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=loading_message.message_id,
        text='Фильм не найден 😔',
    )
    return ConversationHandler.END


async def show_movies_without_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE, search_results: list):
    message = get_search_results_movies_message(search_results)
    context.user_data['search_results'] = search_results
    await update.message.reply_text(message, reply_markup=build_results_navigation_keyboard_without_pagination())
    await update.message.reply_text('Введите номер фильма:')
    return SEARCH_RESULT


async def show_movies_with_pagination(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    search_results: list,
    pagination_start_range: int = 0,
    pagination_end_range: int = 5,
):
    if update.callback_query is not None:
        query = update.callback_query
        message = get_search_results_movies_message(
            search_results[pagination_start_range:pagination_end_range],
            start_pos=pagination_start_range + 1,
        )
        reply_markup = build_results_navigation_keyboard_with_pagination(
            pagination_start_range=pagination_start_range,
            pagination_end_range=pagination_end_range,
            total_results=len(search_results),
        )
        await query.edit_message_text(message, reply_markup=reply_markup)
        return SEARCH_RESULT

    message = get_search_results_movies_message(search_results[pagination_start_range:pagination_end_range])
    reply_markup = build_results_navigation_keyboard_with_pagination(
        pagination_start_range=pagination_start_range,
        pagination_end_range=pagination_end_range,
        total_results=len(search_results),
    )
    context.user_data['search_results'] = search_results
    await update.message.reply_text(message, reply_markup=reply_markup)
    await update.message.reply_text('Введите номер фильма:')
    return SEARCH_RESULT


async def select_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = int(update.message.text)
        results = context.user_data.get('search_results', [])
        if user_input == 0:
            return ConversationHandler.END
        if 1 <= user_input <= len(results):
            message = get_search_result_movies_message(results[user_input - 1])
            reply_markup = build_download_movie_keyboard()
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text('Неверный номер. Попробуй еще раз.')

    except ValueError:
        await update.message.reply_text('Введите корректный номер.')
    return SEARCH_RESULT


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected = context.user_data.get('selected_movie', {})

    if query.data == 'download':
        return await confirm_download_file(update, context, selected)

    elif query.data == 'another':
        await context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id
        )
        return await movie_name_enter(update, context)

    elif query.data == 'done':
        await query.edit_message_text('Завершено. Спасибо за использование!')
        return ConversationHandler.END
    elif 'next' in query.data:
        pagination_start_range = int(query.data.split('next_')[1])
        results = context.user_data.get('search_results', [])
        return await show_movies_with_pagination(
            update,
            context,
            search_results=results,
            pagination_start_range=pagination_start_range,
            pagination_end_range=pagination_start_range + PAGINATION_STEP,
        )
    elif 'prev' in query.data:
        results = context.user_data.get('search_results', [])
        pagination_end_range = int(query.data.split('prev_')[1])
        return await show_movies_with_pagination(
            update,
            context,
            search_results=results,
            pagination_start_range=pagination_end_range - PAGINATION_STEP,
            pagination_end_range=pagination_end_range,
        )
    elif query.data == 'in_start':
        results = context.user_data.get('search_results', [])
        return await show_movies_with_pagination(
            update,
            context,
            search_results=results,
        )


async def confirm_download_file(update: Update, context: ContextTypes.DEFAULT_TYPE, selected):
    download_movie(selected)
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands([
        BotCommand('search', 'Искать кино'),
    ])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Отменено.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def run_bot():
    application = Application.builder().token(os.getenv("TOKEN")).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search', movie_name_enter)],
        states={
            MOVIE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, movies_link_search)],
            SEARCH_RESULT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, select_movie),
                CallbackQueryHandler(button_handler)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)

    await application.initialize()
    await application.updater.start_polling()
    await application.start()
