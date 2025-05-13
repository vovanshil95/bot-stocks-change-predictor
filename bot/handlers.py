from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import COMPANY_DESCRIPTIONS
from utils import plot_forecast, plot_stock_data, get_stock_data, forecast_stock


def get_message_obj(update):
    if update.message:
        return update.message
    elif update.callback_query:
        return update.callback_query.message
    return None


async def handle_ticker(update: Update, context: CallbackContext):
    ticker = update.message.text.upper()
    if ticker not in COMPANY_DESCRIPTIONS:
        await update.message.reply_text("Тикер не найден. Введите один из: 'VTBR', 'GAZP', 'SBER', 'NVTK', 'ROSN'")
        return
    
    context.user_data['ticker'] = ticker
    keyboard = [
        [InlineKeyboardButton("📈 Прогноз", callback_data='forecast'),
         InlineKeyboardButton("📊 График", callback_data='graph')],
        [InlineKeyboardButton("🔄 Выбрать другой тикер", callback_data='change_ticker')]
    ]
    
    await update.message.reply_text(
        COMPANY_DESCRIPTIONS[ticker],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'forecast':
        await handle_forecast(update, context)
    elif query.data == 'graph':
        await handle_graph(update, context)
    elif query.data == 'change_ticker':
        await start(update, context)


async def start(update: Update, context: CallbackContext):
    message = get_message_obj(update)
    await message.reply_text("Введите тикер интересующей акции из списка: 'VTBR', 'GAZP', 'SBER', 'NVTK', 'ROSN'")


async def handle_graph(update: Update, context: CallbackContext):
    message = get_message_obj(update)
    ticker = context.user_data.get('ticker')
    if not ticker:
        await message.reply_text("Сначала выберите тикер.")
        return
    df = get_stock_data(ticker)
    if df is None:
        await message.reply_text("Не удалось получить данные. Попробуйте позже.")
        return
    plot_buf = plot_stock_data(df, ticker)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=plot_buf)


async def handle_forecast(update: Update, context: CallbackContext):
    message = get_message_obj(update)
    ticker = context.user_data.get('ticker')
    if not ticker:
        await message.reply_text("Сначала выберите тикер.")
        return
    df = get_stock_data(ticker)
    if df is None:
        await message.reply_text("Не удалось получить данные. Попробуйте позже.")
        return
    
    await message.reply_text("Идёт парсинг новостей за сегодня, это может занять около минуты.")
    future_X, future_y = await forecast_stock(df, ticker, message)
    plot_buf = plot_forecast(df, future_X, future_y, ticker)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=plot_buf)


async def handle_another_ticker(update: Update, context: CallbackContext):
    start(update, context)
