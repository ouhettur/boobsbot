from telegram import InlineQueryResultCachedMpeg4Gif, InlineQueryResultCachedPhoto
from dao import find_random_media, save_inline_query
import uuid


def inline_query(bot, update):
    query = update.inline_query.query
    telegram_id = update.inline_query.from_user.id
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
    save_inline_query(query, telegram_id)
