import ast
from dao import find_user_id_by_telegram_id, put_report, put_show_mark, justify_img, archive_img


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