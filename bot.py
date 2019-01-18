import logging
import uuid
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,
                          CallbackQueryHandler, InlineQueryHandler)
from commands.admin import show_reported_img
from commands.common import start, initiation_media, info, show_top_img
from config import token
from s3 import upload_to_s3
from commands.inline_query import inline_query
from commands.callback_query import button
from dao import find_user_id_by_telegram_id, save_img

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

GET_IMG = range(1)

reply_keyboard = [['/next', '/upload', '/info']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def send_reply_upload_advice(bot, update):
    if update.message.chat.type == 'private':
        update.message.reply_text('Send a picture, gif or mp4 file < 10 megabytes with new tits.\n'
                                  'Please upload pictures of the desired subject. \nWe do not accept '
                                  'pussy, porn, no boobs content.',
                                  reply_markup=markup)
        return GET_IMG


def get_img(bot, update):
    print(update.message)
    telegram_file_id = update.message.photo[-1].file_id
    print(telegram_file_id)
    file = bot.get_file(file_id=telegram_file_id)
    name = f'{str(uuid.uuid4())}.jpg'
    file.download(f'temp_media/{name}')
    telegram_id = update.message.chat.id
    user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
    save_img(user_id=user_id, img_name=name, media_type='img', telegram_file_id=telegram_file_id)
    update.message.reply_text("upload completed")
    upload_to_s3(img_name=name)
    return ConversationHandler.END


def get_animation(bot, update):
    print(update.message)
    telegram_file_id = update.message.animation.file_id
    file = bot.get_file(file_id=telegram_file_id)
    name = f'{str(uuid.uuid4())}.mp4'
    file.download(f'temp_media/{name}')
    telegram_id = update.message.chat.id
    user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
    save_img(user_id=user_id, img_name=name, media_type='animation', telegram_file_id=telegram_file_id)
    update.message.reply_text("upload completed")
    upload_to_s3(img_name=name)
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def boobs_bot():
    updater = Updater(token)
    dp = updater.dispatcher
    upload_handler = ConversationHandler(
        entry_points=[CommandHandler('upload', send_reply_upload_advice)],

        states={
            GET_IMG: [MessageHandler(Filters.photo, get_img),
                      MessageHandler(Filters.animation, get_animation)]

        },
        fallbacks=[MessageHandler(Filters.document, send_reply_upload_advice),
                   CommandHandler('upload', send_reply_upload_advice)]
    )
    dp.add_handler(upload_handler)
    dp.add_handler(CommandHandler('admin', show_reported_img))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('next', initiation_media))
    dp.add_handler(CommandHandler('top', show_top_img))
    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(InlineQueryHandler(inline_query))
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    boobs_bot()
