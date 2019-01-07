import logging
import uuid
import ast
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedPhoto,
                      InlineQueryResultCachedMpeg4Gif)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,
                          CallbackQueryHandler, InlineQueryHandler)
from dao import *
from config import token
from s3 import upload_to_s3

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

GET_IMG, SHOW_REPORTS = range(2)

reply_keyboard = [['/next', '/upload', '/info']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def start(bot, update):
    print(update.message)
    telegram_id = update.message.chat.id
    if update.message.chat.type == 'private':
        if not is_telegram_id_exists(telegram_id):
            first_name = update.message.from_user.first_name
            last_name = update.message.from_user.last_name
            login = update.message.from_user.username
            language_code = update.message.from_user.language_code
            add_user_by_telegram(telegram_id, first_name, last_name, login, language_code)
            update.message.reply_text(
                'Now you are in the best boobs telegram bot! '
                'You can use this bot in other conversations via inline command @boobsbot_bot .'
                'And also you can add the bot to chats and groups to please interlocutors cool pictures 🍓.')
        update.message.reply_text(
            "Use menu commands!", reply_markup=markup)
    elif update.message.chat.type == 'group' or 'supergroup':
        if not is_telegram_id_exists(telegram_id):
            chat_name = update.message.chat.title
            add_chat_by_telegram(telegram_id, chat_name)
            bot.sendMessage(chat_id=telegram_id, text="Now the bot works in this chat!")
        bot.sendMessage(chat_id=telegram_id, text="Use the /next command to call boobs to this chat")


def initiation_media(bot, update):
    telegram_id = update.message.chat.id
    if update.message.chat.type == 'private':
        user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
        img = find_random_available_media(user_id=user_id)
        if img is None:
            update.message.reply_text('Try later, and we will try to find Boobs for you.\
                                       Help the community and download new boobs by command /upload',
                                      reply_markup=markup)
        else:
            telegram_file_id = img.telegram_file_id
            img_id = img.id
            keyboard = [[InlineKeyboardButton("like", callback_data="{'img_id': %s, 'mark': 1}" % img_id),
                         InlineKeyboardButton("dislike", callback_data="{'img_id': %s, 'mark': -1}" % img_id),
                         InlineKeyboardButton("report", callback_data="{'img_id': %s, 'mark': 0}" % img_id)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if img.media_type == 'img':
                bot.send_photo(chat_id=telegram_id, photo=telegram_file_id,
                               reply_markup=reply_markup,
                               caption=f'Total rating: {img.sum_rating} 🍑')
            elif img.media_type == 'animation':
                bot.send_animation(chat_id=telegram_id, animation=telegram_file_id,
                                   reply_markup=reply_markup,
                                   caption=f'Total rating: {img.sum_rating} 🍑')
            save_show(img_id=img.id, user_id=user_id)
    elif update.message.chat.type == 'group' or 'supergroup':
        if is_telegram_id_exists(telegram_id):
            user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
            img = find_random_available_media(user_id=user_id)
            if img is None:
                bot.sendMessage(chat_id=telegram_id, text='Try later, and we will try to find Boobs for you.\
                                       Help the community and download new boobs by command /upload in personal chat')
            else:
                telegram_file_id = img.telegram_file_id
                if img.media_type == 'img':
                    bot.send_photo(chat_id=telegram_id, photo=telegram_file_id,
                                   caption=f'Total rating: {img.sum_rating} 🍑')
                elif img.media_type == 'animation':
                    bot.send_animation(chat_id=telegram_id, animation=telegram_file_id,
                                       caption=f'Total rating: {img.sum_rating} 🍑')
                save_show(img_id=img.id, user_id=user_id)
        else:
            bot.sendMessage(chat_id=telegram_id, text='To start, activate the bot with the /start command')


def send_reply_upload_advice(bot, update):
    if update.message.chat.type == 'private':
        update.message.reply_text('Send a picture, gif or mp4 file < 10 megabytes with new tits. Warning: no porn!',
                                  reply_markup=markup)
        return GET_IMG


def info(bot, update):
    if update.message.chat.type == 'private':
        telegram_id = update.message.chat.id
        user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
        count_img_upload = count_user_upload(user_id=user_id)
        count_user_img_was_liked = count_user_img_liked(user_id=user_id)
        count_user_img_was_disliked = count_user_img_disliked(user_id=user_id)
        update.message.reply_text(f'You have uploaded {count_img_upload} pictures \n'
                                  f'Your pictures were liked {count_user_img_was_liked} times\n'
                                  f'Your pictures were disliked {count_user_img_was_disliked} times',
                                  reply_markup=markup)


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


def button(bot, update):
    query = update.callback_query
    data = ast.literal_eval(update.callback_query.data)
    print(query)
    print(data['img_id'])
    print(data['mark'])
    user_id = find_user_id_by_telegram_id(telegram_id=update.callback_query.message.chat.id)
    if data['mark'] == 0:
        bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption=f'You sent a report'
        )
        bot.answer_callback_query(callback_query_id=query.id, text=f"You sent a report")
        put_report(img_id=data['img_id'], user_id=user_id)

    elif data['mark'] == 1 or data['mark'] == -1:
        vote = '👎'
        if data['mark'] == 1:
            vote = '👍'
        bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption=f'You put {vote} '
        )
        bot.answer_callback_query(callback_query_id=query.id, text=f"You put {vote}")
        put_show_mark(img_id=data['img_id'], mark=data['mark'], user_id=user_id)
    elif data['mark'] == 2:
        justify_img(img_id=data['img_id'])
        bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption='Пикча помилована'
        )
        bot.answer_callback_query(callback_query_id=query.id, text="Вы помиловали пикчу")
    elif data['mark'] == 3:
        archive_img(img_id=data['img_id'])
        bot.edit_message_caption(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            caption='Пикча архивирована'
        )
        bot.answer_callback_query(callback_query_id=query.id, text="Вы архивировали пикчу")


def show_top_img(bot, update):
    telegram_id = update.message.chat.id
    if update.message.chat.type == 'private':
        user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
        imgs = find_top_media(user_id=user_id)
        for img in imgs:
            if img.rating == 1:
                text = 'You liked boobs'
            elif img.rating == -1:
                text = 'You disliked it'
            elif img.user_id == user_id:
                text = 'This is your image 👋'
            else:
                text = 'You didn\'t rate it'
            telegram_file_id = img.telegram_file_id
            if img.media_type == 'img':
                bot.send_photo(chat_id=telegram_id, photo=telegram_file_id,
                               caption=f'Total rating: {img.sum_rating} 🍑 \nNumber of ratings: {img.count_rating} \n{text}')
            elif img.media_type == 'animation':
                bot.send_animation(chat_id=telegram_id, animation=telegram_file_id,
                                   caption=f'Total rating: {img.sum_rating} 🍑 \nNumber of ratings: {img.count_rating} \n{text}')


def show_reported_img(bot, update):
    telegram_id = update.message.chat.id
    if find_user_role(telegram_id) != 'admin':
        update.message.reply_text("Not enough rights")
        return
    count = count_reported_img()
    update.message.reply_text(f"{count} new images with complaints.")
    reported_imgs = all_reported_img()
    for img in reported_imgs:
        img_id = img.id
        telegram_file_id = img.telegram_file_id

        keyboard = [[InlineKeyboardButton("to justify", callback_data="{'img_id': %s, 'mark': 2}" % img_id),
                     InlineKeyboardButton("to archive", callback_data="{'img_id': %s, 'mark': 3}" % img_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if img.media_type == 'img':
            bot.send_photo(chat_id=telegram_id, photo=telegram_file_id,
                           reply_markup=reply_markup,
                           caption=f'Total rating: {img.sum_rating} 🍑')
        elif img.media_type == 'animation':
            bot.send_animation(chat_id=telegram_id, animation=telegram_file_id,
                               reply_markup=reply_markup,
                               caption=f'Total rating: {img.sum_rating} 🍑')


def inlinequery(bot, update):
    query = update.inline_query.query
    results = []
    for media in find_random_media(count=7):
        if media.media_type == 'img':
            results.append(InlineQueryResultCachedPhoto(type='photo',
                                                        id=uuid.uuid4(),
                                                        photo_file_id=media.telegram_file_id))
        elif media.media_type == 'animation':
            results.append(InlineQueryResultCachedMpeg4Gif(type='mpeg4_gif',
                                                           id=uuid.uuid4(),
                                                           mpeg4_file_id=media.telegram_file_id))

    update.inline_query.answer(results, next_offset=7, cache_time=0)


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

    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    boobs_bot()
