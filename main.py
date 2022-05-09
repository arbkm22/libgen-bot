import os
import logging
from typing import Text
from telegram.ext import Updater, dispatcher, updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, replymarkup, ForceReply, update
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from libgen import libgen, dlLinkGrabber
from telegram_bot_pagination import InlineKeyboardPaginator
# loading environment variables
# uncomment this if you want to test locally
# but first make a .env file and save the token there

""" 
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")
"""

# heroku vars
TOKEN = os.environ.get("TOKEN")
MY_ID = os.environ.get("MY_ID")

# ------ Global Variables ------
BOOKS = {}

# -----------------LOGGING-------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
logger.info(msg="Logging started...")


# dictionary to text


def transform(data):
    tempList = []
    for item in data:
        link = item['link']
        link = dlLinkGrabber(link)
        text = "Link"
        t = f"""
*Title*     : `{item['title']}`
*Author*    : `{item['author']}`
*Language*  : `{item['lang']}`
*Format*    : `{item['ext']}`
*Size*      : `{item['size']}`
*Download*  :  [{text}]({link})
"""
        tempList.append(t)
    return tempList


# Start function: when the bot starts
def start(update, context):
    usr_id = update.effective_chat.id
    if (usr_id != MY_ID):
        context.bot.sendMessage(chat_id=MY_ID,
        text=f"Start function used by `{usr_id}`")
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=f"""
Hey! To download a book use\n`/book` followed by the name of the book.
To know more about the bot use `/about`.
To show this dialogue use `/help`.
P.S: To read certain file types, download a book reader i.e., ReadEra, Moon+ Reader""",
                            parse_mode="Markdown")

# book function: gets the name of the book and pass it to the scraper
def book(update, context):
    # BOOKS = {}
    global BOOKS
    bookName = " ".join(context.args)
    usr_id = update.effective_chat.id
    if (usr_id != MY_ID):
            context.bot.sendMessage(chat_id=MY_ID,
            text=f"`{usr_id}` searched for `{bookName}`")
    # context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"You entered {bookName}")
    if len(bookName) < 1:
        update.message.reply_text("Enter the name of the book: ",
                                  reply_markup=ForceReply(force_reply=True, selective=True))
        return 0
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=f"Searching for book `{bookName}` in database, please wait...",
                                parse_mode="Markdown")
        data = libgen(bookName)
        if len(data) > 0:
            uuid = str(update.effective_chat.id) + \
                str(update.effective_user.id)
            BOOKS[uuid] = transform(data)
            paginator = InlineKeyboardPaginator(
                len(data),
                data_pattern='book#{page}'
            )

            message = context.bot.sendMessage(
                chat_id=update.message.chat_id,
                text=BOOKS[uuid][0],
                reply_markup=paginator.markup,
                parse_mode="Markdown",
            )
        else:
            context.bot.sendMessage(chat_id=update.effective_chat.id,
                                    text="No book found.")
        return ConversationHandler.END


# Conversation handler for the above function
def book_conv(update, context):
    global BOOKS
    bookName = update.message.text
    if len(bookName) < 1:
        update.message.reply_text("Enter the name of the book: ",
                                  reply_markup=ForceReply(force_reply=True, selective=True))
        return 0
    else:
        context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=f"Searching for book `{bookName}` in database, please wait...",
                                parse_mode="Markdown")
        data = libgen(bookName)
        if len(data) > 0:
            uuid = str(update.effective_chat.id) + \
                str(update.effective_user.id)
            BOOKS[uuid] = transform(data)
            paginator = InlineKeyboardPaginator(
                len(data),
                data_pattern='book#{page}'
            )

            message = context.bot.sendMessage(
                chat_id=update.message.chat_id,
                text=BOOKS[uuid][0],
                reply_markup=paginator.markup,
                parse_mode="Markdown",
            )
        else:
            context.bot.sendMessage(chat_id=update.effective_chat.id,
                                    text="No book found.")
        return ConversationHandler.END


# callback funtion: required for pagination
def book_callback(update, context):
    global BOOKS
    uuid = str(update.effective_chat.id) + str(update.effective_user.id)
    query = update.callback_query
    query.answer("loading")
    page = int(query.data.split('#')[1])

    paginator = InlineKeyboardPaginator(
        page_count=len(BOOKS[uuid]),
        current_page=page,
        data_pattern="book#{page}"
    )

    query.edit_message_text(
        text=BOOKS[uuid][page - 1],
        reply_markup=paginator.markup,
        parse_mode="Markdown"
    )


def about(update, context):
    usr_id = update.effective_chat.id
    if (usr_id != MY_ID):
        context.bot.sendMessage(chat_id=MY_ID,
        text=f"About used by `{usr_id}`")
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=f"""This is a bot made by scraping the site libgen.rs
For any queries or support contact @bhaskar_mahto""")


def cancel(update, context):
    update.message.reply_text("Task cancelled.")
    return ConversationHandler.END


def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Start handler
    dispatcher.add_handler(CommandHandler("start", start, run_async=True))

    # Conversation handler
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("book", book, run_async=True)],
        states={
            0: [MessageHandler(Filters.text & ~Filters.command, book_conv, run_async=True)]
        },
        fallbacks=[CommandHandler("cancel", cancel, run_async=True)]
    ))

    # CallbackQueryHandler for the book_callback
    dispatcher.add_handler(CallbackQueryHandler(
        book_callback, pattern="^book#", run_async=True))
    # About
    dispatcher.add_handler(CommandHandler("about", about, run_async=True))
    # Help
    dispatcher.add_handler(CommandHandler("help", start, run_async=True))

    # everything goes above this
    # start/end bot
    # ------ System Polling ------
    updater.start_polling() # switched from web to worker, for better uptime
    # ------ Heroku Webhook ------
    # PORT = int(os.environ.get("PORT", 5000))
    # URL = "https://libgen-book-bot.herokuapp.com/"
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=TOKEN, webhook_url=URL+TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
