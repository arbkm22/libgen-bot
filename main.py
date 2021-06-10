import os, logging
from telegram.ext import Updater, dispatcher, updater, CommandHandler

# loading environment variables
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

def start(update, context):
    context.bot.sendMessage(chat_id=update.effective_chat.id, text="Started")

def main() -> None:
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    dispatcher.add_handler(start_handler)

    # everything goes above this
    # start/end bot
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()