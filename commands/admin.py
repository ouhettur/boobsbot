from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from dao import find_user_role, count_reported_img, all_reported_img


def show_reported_img(bot, update):
    telegram_id = update.message.chat.id
    if find_user_role(telegram_id) != 'admin':
        update.message.reply_text("Not enough rights")
        return

    update.message.reply_text(f"{count_reported_img()} new images with complaints.")
    for img in all_reported_img():
        send_img(bot, img, telegram_id, img.telegram_file_id)


def send_img(bot, img, telegram_id, telegram_file_id):
    reply_markup = prepare_reply_markup(img.id)
    caption = f'Total rating: {img.sum_rating} 🍑'
    if img.media_type == 'img':
        bot.send_photo(chat_id=telegram_id, photo=telegram_file_id, reply_markup=reply_markup, caption=caption)
    elif img.media_type == 'animation':
        bot.send_animation(chat_id=telegram_id, animation=telegram_file_id, reply_markup=reply_markup, caption=caption)
    else:
        raise NotImplementedError()


def prepare_reply_markup(img_id):
    keyboard = [[
        InlineKeyboardButton("to justify", callback_data="{'img_id': %s, 'mark': 2}" % img_id),
        InlineKeyboardButton("to archive", callback_data="{'img_id': %s, 'mark': 3}" % img_id)
    ]]
    return InlineKeyboardMarkup(keyboard)
