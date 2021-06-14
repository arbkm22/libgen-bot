import os, logging
from telegram.ext import Updater, dispatcher, updater, CommandHandler
from libgen import libgen
from telegram_bot_pagination import InlineKeyboardPaginator
# loading environment variables
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Start function: when the bot starts
def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Started")

# book function: gets the name of the book and pass it to the api
def book(update, context):
    bookName = " ".join(context.args)
    # context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"You entered {bookName}")
    data = libgen(bookName)


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start handler
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))

    # Book handler (gets the name of the book)
    dispatcher.add_handler(CommandHandler("book", book, run_async=True))

    # everything goes above this
    # start/end bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()