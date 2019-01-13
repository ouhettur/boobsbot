from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from dao import *

reply_keyboard = [['/next', '/upload', '/info']]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


def start(bot, update):
    print(update.message)
    telegram_id = update.message.chat.id
    if update.message.chat.type == 'private':
        private_start(bot, update, telegram_id)
    elif update.message.chat.type == 'group' or 'supergroup':
        group_start(bot, update, telegram_id)


def private_start(bot, update, telegram_id):
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


def group_start(bot, update, telegram_id):
    if not is_telegram_id_exists(telegram_id):
        chat_name = update.message.chat.title
        add_chat_by_telegram(telegram_id, chat_name)
        bot.sendMessage(chat_id=telegram_id, text="Now the bot works in this chat!")
    bot.sendMessage(chat_id=telegram_id, text="Use the /next command to call boobs to this chat")


def initiation_media(bot, update):
    telegram_id = update.message.chat.id
    if is_telegram_id_exists(telegram_id):
        user_id = find_user_id_by_telegram_id(telegram_id=telegram_id)
        send_media(bot, update, user_id, telegram_id)
    else:
        bot.sendMessage(chat_id=telegram_id, text='To start, activate the bot with the /start command')


def send_media(bot, update, user_id, telegram_id):
    img = find_random_available_media(user_id=user_id)
    if img is None:
        bot.sendMessage(chat_id=telegram_id, text='Try later, and we will try to find Boobs for you.\
                               Help the community and download new boobs by command /upload in personal chat')
    else:
        telegram_file_id = img.telegram_file_id
        img_id = img.id
        chat_type = update.message.chat.type
        reply_markup = create_keyboard(chat_type, img_id)
        if img.media_type == 'img':
            bot.send_photo(chat_id=telegram_id, photo=telegram_file_id,
                           reply_markup=reply_markup,
                           caption=f'Total rating: {img.sum_rating} 🍑')
        elif img.media_type == 'animation':
            bot.send_animation(chat_id=telegram_id, animation=telegram_file_id,
                               reply_markup=reply_markup,
                               caption=f'Total rating: {img.sum_rating} 🍑')
        save_show(img_id=img.id, user_id=user_id)


def create_keyboard(chat_type, img_id):
    print(chat_type * 100)
    if chat_type == 'private':
        keyboard = [[InlineKeyboardButton("like", callback_data="{'img_id': %s, 'mark': 1}" % img_id),
                     InlineKeyboardButton("dislike", callback_data="{'img_id': %s, 'mark': -1}" % img_id),
                     InlineKeyboardButton("report", callback_data="{'img_id': %s, 'mark': 0}" % img_id)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        return reply_markup
    elif chat_type == 'group' or 'supergroup':
        return None

