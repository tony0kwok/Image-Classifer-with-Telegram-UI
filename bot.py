import redis
from redis import StrictRedis
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

import threading
import time
from PIL import Image
import requests
from io import BytesIO
import base64
import json
import struct
import re
import urllib

#put your bot token here
token = "791232441:AAHQVnJGmZG9pCklVc-zZwdm2WkCG9USXdM"

def is_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def is_url_image(url):
    res = urllib.request.urlopen(url)
    http_message = res.info()
    main = http_message["Content-Type"]
    return main.startswith("image")

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
pool = redis.ConnectionPool(host='localhost', port=6379)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    if is_url(update.message.text):
        if is_url_image(update.message.text):
            data = {}
            """Echo the user message."""
            update.message.reply_text("image is handling...")
            r = StrictRedis(connection_pool=pool)
            data["url"] = update.message.text
            data["chat_id"] = update.message.chat.id
            message = json.dumps(data)
            r.rpush('download', message.encode("utf-8"))

def show(bot, update):
    '''
    data = {}
    r = StrictRedis(connection_pool=pool)
    data["img_id"] = update.message.photo[-1].file_id
    data["chat_id"] = update.message.chat.id
    message = json.dumps(data)
    r.rpush('download', message.encode("utf-8"))
    update.message.reply_text("image is received")
    '''
    
    update.message.reply_text("image is handling...")
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    photo_file.download('user_photo.jpg')
    with open('user_photo.jpg', 'rb') as outfile:
        raw_image = outfile.read()
        encoded_image = base64.b64encode(raw_image)
        base64_string = encoded_image.decode('utf-8')

    data = {}
    r = StrictRedis(connection_pool=pool)
    data["img_id"] = base64_string
    data["chat_id"] = update.message.chat.id
    message = json.dumps(data)
    r.rpush('download', message.encode("utf-8"))
    

def putpd(bot, update):
    r = StrictRedis(connection_pool=pool)
    prediction = [{"label": "container_ship", "score": 0.4625}, {"label": "lifeboat", "score": 0.1579}]
    chat_id = 753102236
    message = json.dumps({"prediction":prediction, "chat_id": chat_id})
    r.rpush('prediction', message.encode("utf-8"))

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

class sendPredictThread (threading.Thread):
    def __init__(self, threadID, name, pool, bot):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.pool = pool
        self.bot = bot
    def run(self):
        print("Starting " + self.name)
        r = StrictRedis(connection_pool=self.pool)
        while True:
            pd = json.loads(r.blpop('prediction')[1].decode("utf-8"))
            self.bot.send_message(pd["chat_id"], text='\n'.join(str(label) for label in pd["predictions"]))
            pd = {}
        print("Exiting " + self.name)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("putpd", putpd))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.photo, show))

    # log all errors
    dp.add_error_handler(error)

    #start the thread that send prediction to user
    t1 = sendPredictThread(123, "Thread-1", pool, updater.bot)
    t1.start()

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
