import string
import vk_api
import re

from datetime import datetime

import DB
import Data

image_ext = ["raw", "jpeg", "jpg", "tiff", "png", "bmp", "gif", "jpeg 2000", "jp2"]
# Данные для взаимодействия в ВКонтакте
token_vk = '57508162575081625750816290572d96de557505750816235ffa96640028a57b51fe0b1'
version_vk = 5.131


def is_vk_group_link(message):
    pattern = r'https?://vk\.com/[a-zA-Z0-9_-]+'
    match = re.search(pattern, message)
    if match:
        return True
    else:
        return False


# функция добавления группы в список отслеживаемых
def return_info_vk_group(message: string):
    returned = []
    try:
        # поиск в сообщении пользователя ссылки
        group = re.findall(r"https[:]{1}/{2}vk[.]{1}com/{1}.*", message)
        for el in group:
            # удаляем ссылку на домен
            tmp = str(el).replace("https://vk.com/", "")
            returned.append(tmp)

            # получаем id группы вк
            group_id = return_group_id(tmp)
            returned.append(group_id)

            # если вернулся 0, то стена недоступна
            if group_id == 0:
                returned.append(0)

            else:
                returned.append(1)
                # происходит добавление группы в базу данных
                group_name = group_get_name(group_id)
                returned.append(group_name)
                return returned
    except:
        print("Неудачная попытка добавления")
        return []


# функция, которая возвращает id указанной группы
def return_group_id(dom):
    try:
        session = vk_api.VkApi(token=token_vk)
        group = session.method("groups.getById", {"group_ids": dom})
        group_id = group[0]['id']
    except:
        print("Группа должна быть открытой, или вы должны быть ее участником")
        group_id = 0
    return group_id


# функция возвращает имя сообщества
def group_get_name(group_id):
    try:
        session = vk_api.VkApi(token=token_vk)
        group = session.method("groups.getById", {"group_ids": group_id})
        group_name = group[0]['name']
    except:
        print("Группа должна быть открытой, или вы должны быть ее участником")
        group_name = ""
    return group_name


def is_valid_file_format(filename):
    valid_formats = ['zip', 'gif', 'pdf']
    file_format = filename.lower().rsplit('.', 1)[-1]
    return file_format in valid_formats


def get_group_post_attachments(item):
    res_photo_ref = ""
    array_attachment = []
    # получаем вложения
    try:
        # пробуем получить вложенные изображения
        photo_ref = item['attachments']
        for attachment in photo_ref:
            if attachment['type'] == 'photo':
                sizes = attachment['photo']['sizes']
                max_height = 0
                max_width = 0
                # Выбираем вложенное изображение максимального качества, т.к. вк хранит сразу много ссылок разного качества одного и того же изображения
                for size in sizes:
                    if size['height'] > max_height and size['width'] > max_width:
                        max_height = size['height']
                        max_width = size['width']
                        res_photo_ref = size['url']
                # print(res_photo_ref)
                array_attachment.append(["image", res_photo_ref])
            if attachment['type'] == 'doc':
                docs_link = attachment['doc']['url']
                docs_title = attachment['doc']['title']
                if is_valid_file_format(docs_title):
                    array_attachment.append(["doc", docs_link, docs_title])
                elif Data.is_image(docs_title):
                    array_attachment.append(["image", docs_link])
                else:
                    array_attachment.append(["other", docs_link, docs_title])
                # print(docs_link)
                # print(docs_title)
    except:
        # пробуем получить вложения из репостнутого поста
        try:
            for item1 in item['copy_history']:
                photo_ref = item1['attachments']
                for attachment in photo_ref:
                    if attachment['type'] == 'photo':
                        sizes = attachment['photo']['sizes']
                        max_height = 0
                        max_width = 0
                        res_photo_ref = None
                        for size in sizes:
                            if size['height'] > max_height and size['width'] > max_width:
                                max_height = size['height']
                                max_width = size['width']
                                res_photo_ref = size['url']
                        # print(res_photo_ref)
                        array_attachment.append(["image", res_photo_ref])
                    if attachment['type'] == 'doc':
                        docs_link = attachment['doc']['url']
                        docs_title = attachment['doc']['title']
                        array_attachment.append(["doc", docs_link, docs_title])
                        # print(docs_link)
        except:
            print("0000000000000000000000000000000")

    return array_attachment


# функция, которая получает текст, и картинки постов из указанной группы
def get_group_post(conn, domain, date_add):
    returned_arr = []

    try:
        session = vk_api.VkApi(token=token_vk)
        vk_id = domain
        domain_tmp = domain
        domain = f"-{domain}"
        post = session.method("wall.get", {"owner_id": domain, "count": 100})
        post_items = post['items']

        count = 0
        for item in post_items:
            # время считываемого поста
            res_time = datetime.fromtimestamp(int(item['date']))

            # время последнего выложенного поста в телеграм
            # date_add_result = datetime.strptime(f"{date_add}", '%Y-%m-%d %H:%M:%S')
            date_add_result = datetime.strptime(f"{date_add}", '%Y-%m-%d %H:%M:%S')
            # если считываемый пост вышел позже, чем последний обработанный пост, то добавляем его в список постов
            # так мы избежим повторного добавления постов
            if res_time > date_add_result:
                print(f"=======================\nПост {count}:\n")
                count += 1
                result_text = ""
                # запоминаем текст поста
                try:
                    for item1 in item['copy_history']:
                        result_text += f"{group_get_name(domain_tmp)}\n\n{item['text']}\nРепост:\n\n{item1['text']}\n\nДата: {res_time:%d-%m-%Y %H:%M:%S %Z}"
                except:
                    result_text += f"{group_get_name(domain_tmp)}\n\n{item['text']}\n\nДата: {res_time:%d-%m-%Y %H:%M:%S %Z}"
                array_attachments = get_group_post_attachments(item)
                vk_post_id = item['id']
                link = f'https://vk.com/wall{domain}_{vk_post_id}'
                returned_arr.append([result_text, array_attachments, res_time, group_get_name(domain_tmp), link,
                                     domain_tmp])
            else:
                continue
        return returned_arr
    except Exception as e:
        print(e)
        return returned_arr


# функция, которая проходится по всем группам из бд
def for_all_group_in_db():
    try:
        session = vk_api.VkApi(token=token_vk)
        vk = session.get_api()
        connection = DB.get_connection()
        select_group = "SELECT * FROM source;"
        groups = DB.answer_on_request(connection, select_group)
        array_posts_groups = []
        for group in groups:
            print(f"Посты из группы: {group[2]}")
            array_posts_groups.append(get_group_post(connection, group[3], group[4]))
        connection.close()
        return array_posts_groups
    except Exception as e:
        print(e)
        return []


def return_link_group(id_group: int):
    return 'https://vk.com/club' + str(id_group)
