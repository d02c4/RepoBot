from telebot import TeleBot
from telebot import types
import Data
import DB
import time


chat_id = "@PNRPU_NEWS"


def send_news_new(bot: TeleBot):
    request = (f"SELECT `post_text_id`, `post_date`, s.`source_id` "
               f"FROM post "
               f"JOIN botdata.source s ON s.source_id = post.source_id "
               f"WHERE `post_date` > `source_date_update` "
               f"ORDER BY `post_date`;")
    conn = DB.get_connection()
    arr_post = DB.answer_on_request(conn=conn, request=request)
    conn.close()
    new_post = True
    try:
        arr_db_update = []
        for post in arr_post:
            request = (f"SELECT user_membership.`user_id` FROM user_membership "
                       f"join botdata.user u on u.user_id = user_membership.user_id "
                       f"join botdata.source s on s.source_id = user_membership.source_id "
                       f"WHERE s.source_id = '{post[2]}';")
            arr_user = DB.return_arr_answer(request=request)
            request = (f"SELECT  `attachment_type`, `attachment_link` FROM attachment "
                       f"JOIN botdata.post p on attachment.post_id = p.post_id "
                       f"WHERE post_text_id = '{post[0]}'")
            conn = DB.get_connection()
            arr_attachment = DB.answer_on_request(conn=conn, request=request)
            conn.close()
            for user in arr_user:
                time.sleep(0.3)
                try:
                    text_mess = bot.copy_message(chat_id=user, from_chat_id=chat_id, message_id=post[0])
                    arr_photo = []
                    arr_doc = []
                    for att in arr_attachment:
                        if att[0] == 'photo':
                            arr_photo.append(att[1])
                        elif att[0] == 'doc' or att[0] == 'other':
                            arr_doc.append(att[1])
                    arr_media_photo = []
                    for photo in arr_photo:
                        arr_media_photo.append(types.InputMediaPhoto(media=photo))
                    if len(arr_media_photo) > 0:
                        bot.send_media_group(chat_id=user, media=arr_media_photo,
                                             reply_to_message_id=text_mess.message_id)

                    arr_media_doc = []
                    for doc in arr_doc:
                        arr_media_doc.append(types.InputMediaDocument(media=doc))
                    if len(arr_media_doc) > 0:
                        bot.send_media_group(chat_id=user, media=arr_media_doc,
                                             reply_to_message_id=text_mess.message_id)
                    new_post = new_post * True
                except Exception as e:
                    new_post = new_post * False
                    print(e)
            if new_post:
                request = (f"UPDATE `source` SET `source_date_update` = '{post[1]}' "
                           f"WHERE `source_id` = '{post[2]}';")
                con = DB.get_connection()
                DB.answer_on_request(conn=con, request=request)
                con.close()
            new_post = True
    except Exception as e:
        print(e)


def send_att(bot: TeleBot):
    file_ids = ['BQACAgQAAx0EYyP3GgACPvVmJsioODXcfw8k7xgESzWZMRRueAACvQUAAqSOPVEfT4mDcZsG6jQE',
                'BQACAgQAAx0EYyP3GgACPvZmJsio86rF33Tw-ZdVCQK5GHwLBAAC8gUAAqR-PFFHWYIdr9w3JjQE',
                'BQACAgQAAx0EYyP3GgACPvdmJsio2ovPVbbp-9RN3QwdkPjaUwACbAUAAnACPVEDFMGHvSyM0zQE',
                'BQACAgQAAx0EYyP3GgACPvhmJsioFYRvkv5P2bR5FPtF7MJy3AACjAUAAsX6PVGNHfjq4SMcNjQE',
                'BQACAgQAAx0EYyP3GgACPvlmJsiodvOCllhSPWOrO1y30W4NVgACmAUAAjZtPVHqA1BU4WfZNjQE']
    att = []
    for id1 in file_ids:
        att.append(types.InputMediaDocument(media=id1))
    bot.send_media_group(chat_id=400457439, media=att)

