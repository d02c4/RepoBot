import vk
from telebot import TeleBot
from telebot import types
from telebot import ExceptionHandler

import Data
import DB
import time
import tgdispatcher

TOKEN = '5370592082:AAENCj51nhzJ-i0iUFlhsoGASbMDqpQduaI'

tele_bot = TeleBot(TOKEN)
chat_id = "@PNRPU_NEWS"


def collect_news():
    array_news = vk.for_all_group_in_db()
    return array_news


# Функция для отправки сообщения с учетом ограничений
def send_message_with_rate_limit(bot, text):
    text = Data.truncate_string(text)
    while True:
        try:
            result = bot.send_message(chat_id=chat_id, text=text, parse_mode='MARKDOWNV2',
                                      disable_web_page_preview=True)
            return result  # Выходим из цикла, если сообщение успешно отправлено
        except Exception as e:
            if "can't parse entities" in str(e):
                try:
                    result = bot.send_message(chat_id=chat_id, text=text, parse_mode=None,
                                              disable_web_page_preview=True)
                    return result
                except Exception as e:
                    result = bot.send_message(chat_id=chat_id, text="Не получилось обработать текст поста",
                                              parse_mode=None,
                                              disable_web_page_preview=True)
                    return result  # Выходим из цикла, если сообщение успешно отправлено

            print("Ожидание отправки сообщения:", e)
            time.sleep(3)  # Ждем некоторое время перед повторной попыткой


# Функция для отправки файлов и изображений с учетом ограничений
def send_file_with_rate_limit(bot: TeleBot, media_group, reply_to_message_id, media_type: str):
    while True:
        try:
            if media_type == 'photo':
                res = bot.send_media_group(chat_id=chat_id, media=media_group,
                                           reply_to_message_id=reply_to_message_id)
            elif media_type == 'doc':
                res = bot.send_media_group(chat_id=chat_id, media=media_group,
                                           reply_to_message_id=reply_to_message_id)
            else:
                res = bot.send_document(chat_id=chat_id, document=types.InputFile(media_group),
                                        reply_to_message_id=reply_to_message_id)
            return res
        except Exception as e:
            print("Ожидание отправки файлов:", e)
            time.sleep(3)  # Ждем некоторое время перед повторной попыткой


# Функция для отправки сообщения и вложений во временный канал, и получение id текста и вложений
def get_send_news_id(array_news):
    array_to_db = []
    Data.del_all_attachments()
    for array_source_news in array_news:
        for news in array_source_news:
            array_attachments = []
            name = Data.escape_reserved_characters(news[3])
            txt = Data.get_vk_hyperlinks_markdown(news[0]) + f'\n[{name}]({news[4]})'
            mess_text = send_message_with_rate_limit(bot=tele_bot, text=txt)
            # mess_text = tele_bot.send_message(chat_id=chat_id, text=news[0])
            # print(news[0])
            arr_photo = []
            media_group_photo = []
            arr_doc = []
            media_group_doc = []
            arr_other = []
            media_group_other = []
            for attachments in news[1]:
                if attachments[0] == 'image':
                    arr_photo.append(types.InputMediaPhoto(media=attachments[1]))
                elif attachments[0] == 'doc':
                    arr_doc.append(types.InputMediaDocument(media=attachments[1]))
                elif attachments[0] == 'other':
                    filename = f'./attachments/{Data.download_file(attachments[1], filename=attachments[2])}'
                    # arr_other.append(types.InputFile(filename))
                    arr_other.append(filename)
            if len(arr_photo) != 0:
                media_group_photo = send_file_with_rate_limit(bot=tele_bot, media_group=arr_photo,
                                                              reply_to_message_id=mess_text.message_id,
                                                              media_type='photo')
            if len(arr_doc) != 0:
                media_group_doc = send_file_with_rate_limit(bot=tele_bot, media_group=arr_doc,
                                                            reply_to_message_id=mess_text.message_id,
                                                            media_type='doc')
            for el in arr_other:
                mess_append_other = send_file_with_rate_limit(bot=tele_bot, media_group=el,
                                                              reply_to_message_id=mess_text.message_id,
                                                              media_type='other')
                media_group_other.append(mess_append_other.document.file_id)
            tmp = []
            for att in media_group_photo:
                tmp.append(att.photo[len(att.photo) - 1].file_id)
            array_attachments.append(['photo', tmp.copy()])
            tmp.clear()
            for att in media_group_doc:
                tmp.append(att.document.file_id)
            array_attachments.append(['doc', tmp.copy()])
            tmp.clear()
            array_attachments.append(['other', media_group_other])
            array_to_db.append([mess_text.message_id, array_attachments, news[2], news[3], news[4], news[5]])
    Data.del_all_attachments()
    return array_to_db


def add_to_db(array_to_db):
    connection = DB.get_connection()
    for posts in array_to_db:
        DB.add_to_database(connection=connection, post_text_id=posts[0],
                           source_id=DB.return_source_id_by_needed_id(posts[5]),
                           post_date=posts[2],
                           post_link=posts[4],
                           array_attachment=posts[1])
    connection.close()


def send_attachments():
    file_ids = ['BQACAgQAAx0EYyP3GgACPvVmJsioODXcfw8k7xgESzWZMRRueAACvQUAAqSOPVEfT4mDcZsG6jQE',
                'BQACAgQAAx0EYyP3GgACPvZmJsio86rF33Tw-ZdVCQK5GHwLBAAC8gUAAqR-PFFHWYIdr9w3JjQE',
                'BQACAgQAAx0EYyP3GgACPvdmJsio2ovPVbbp-9RN3QwdkPjaUwACbAUAAnACPVEDFMGHvSyM0zQE',
                'BQACAgQAAx0EYyP3GgACPvhmJsioFYRvkv5P2bR5FPtF7MJy3AACjAUAAsX6PVGNHfjq4SMcNjQE',
                'BQACAgQAAx0EYyP3GgACPvlmJsiodvOCllhSPWOrO1y30W4NVgACmAUAAjZtPVHqA1BU4WfZNjQE']
    att = []
    for id1 in file_ids:
        att.append(types.InputMediaDocument(media=id1))
    tele_bot.send_media_group(chat_id=400457439, media=att)


def main():
    while True:
        time.sleep(5)
        add_to_db(get_send_news_id(collect_news()))
        tgdispatcher.send_news_new(tele_bot)


main()
