import os, logging
from typing import Text
from requests.models import parse_header_links
from telegram.ext import Updater, dispatcher, updater, CommandHandler, CallbackQueryHandler
from libgen import libgen, dlLinkGrabber
from telegram_bot_pagination import InlineKeyboardPaginator
# loading environment variables
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ---GLOBAL VARiABLES---
BOOKS = []

# dictionary to text
def transform(data):
    global BOOKS
    BOOKS = []
    for item in data:
        link = item['link']
        # link = dlLinkGrabber(link)
        t = f"""
*Title*     : `{item['title']}`
*Author*    : `{item['author']}`
*Language*  : `{item['lang']}`
*Link*      : `{link}`
"""
        BOOKS.append(t)

    
# Start function: when the bot starts
def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Started")

# book function: gets the name of the book and pass it to the api
def book(update, context):
    global BOOKS
    bookName = " ".join(context.args)
    # context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"You entered {bookName}")
    data = libgen(bookName)
    if len(data) > 0:
        transform(data)

        paginator = InlineKeyboardPaginator(
            len(data),
            data_pattern='book#{page}'
        )

        message = context.bot.sendMessage(
            chat_id=update.message.chat_id,
            text=BOOKS[0],
            reply_markup=paginator.markup,
            parse_mode="Markdown",
        )

def book_callback(update, context):
    global BOOKS
    query = update.callback_query   
    query.answer("loading")
    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        page_count=len(BOOKS),
        current_page=page,
        data_pattern="book#{page}"
    )

    query.edit_message_text(
        text=BOOKS[page - 1],
        reply_markup=paginator.markup,
        parse_mode="Markdown"
    )


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start handler
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))

    # Book handler (gets the name of the book)
    dispatcher.add_handler(CommandHandler("book", book, run_async=True))

    # CallbackQueryHandler for the book_callback
    dispatcher.add_handler(CallbackQueryHandler(
        book_callback, pattern="^book#", run_async=True))
    

    # everything goes above this
    # start/end bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()