from telegram.ext import CommandHandler, MessageHandler, filters, Application, CallbackQueryHandler

from config import BOT_TOKEN
from handlers import handle_ticker, button_handler, start


def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ticker))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == '__main__':
    main()
