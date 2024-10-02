import DB
import os
import wget
from telegram.helpers import escape_markdown
import telebot.formatting as Format

import re
from pymysql import connect, Error

# Данные для взаимодействия в ВКонтакте
token_vk = '57508162575081625750816290572d96de557505750816235ffa96640028a57b51fe0b1'
version_vk = 5.131
# массив расширений изображений
image_ext = ["raw", "jpeg", "jpg", "tiff", "png", "bmp", "gif", "jpeg 2000", "jp2"]

# Данные для взаимодействия с Telegram
API_TOKEN_TG = '5370592082:AAENCj51nhzJ-i0iUFlhsoGASbMDqpQduaI'
chat_id = "PNRPU_news_bot"


# # Данные для взаимодействия с базой данных
# db_host = "127.0.0.1"
# db_port = 3306
# db_username = "root"
# db_userpass = "132432"
# db_name = "TgDB"


# Возвращает тип файла
def get_type_of_file(filename: str):
    if filename.__contains__("."):
        ext = filename[filename.rfind(".") + 1:]
        if ext != "":
            return ext
    return "None"


# проверка на изображение
def is_image(filename: str):
    if filename != "":
        t = get_type_of_file(filename)
        for ext in image_ext:
            if t == ext:
                return True
    return False


# функция добавления группы в список отслеживаемых
def add_group(group_info: []):
    try:
        if group_info[2] == 0:
            print('Группы не существует')
            return 0
        else:
            # происходит добавление группы в базу данных
            # ['skrillex_rus', 24363586, 1, 'Skrillex']
            group_id = group_info[1]
            group_name = group_info[3]
            print(group_id, group_name)
            lnk = 'https://vk.com/club' + str(group_id)
            request = f"INSERT INTO `source` (`source_needed_id`, `source_name`, `source_link`) VALUES ('{group_id}', '{group_name}', '{lnk}')"
            connection = DB.get_connection()
            DB.answer_on_request(connection, request)
            connection.close()
            return 1
    except:
        print("Неудачная попытка добавления")


def download_attachment(link: str, filename: str):
    memory_path = os.getcwd()
    os.chdir('./attachments')
    try:
        if filename != "":
            wget.download(link, filename)
        else:
            wget.download(link)
        os.chdir(memory_path)
    except:
        print(f"Неудачная попытка скачивания {link}")
        os.chdir(memory_path)


# Скачивание списка вложений
def downloads_all_attachments(arr_attachments: list):
    for attachment in arr_attachments:
        download_attachment(attachment)


# получение списка вложений
def get_attachments_list():
    try:
        memory_path = os.getcwd()
        os.chdir('./attachments')
        data_list = os.listdir()
        os.chdir(memory_path)
        return data_list
    except:
        print("неудачная попытка получения списка файлов")


# удаление всех вложений
def del_all_attachments():
    attachments = get_attachments_list()
    memory_path = os.getcwd()
    os.chdir('./attachments')
    try:
        for attachment in attachments:
            os.remove(attachment)
        print("Все вложения успешно удалены")
    except:
        print("При удалении произошла ошибка!")
    os.chdir(memory_path)


# Скачивает файл и возвращает его название
def download_file(link: str, filename: str):
    try:
        l1 = get_attachments_list()
        download_attachment(link, filename)
        l2 = get_attachments_list()
        l2 = set(l2) - set(l1)
        print(f"Файл {l2} был скачан")
        return l2.pop()
    except:
        print("Произошла ошибка при попытке скачать файл")
        return ''


def escape_reserved_characters(text):
    return text.replace('|', ' ')


def truncate_string(text: str) -> str:
    if len(text) > 4096:
        return text[:4096]
    return text


# изменение ссылок на группы
def get_right_text(text: str):
    tmp_text = text
    try:
        # в тексте находятся ссылки
        tmp_arr = re.findall(r'[[]{1}[a-z]*?\d*?[|].*?\]{1}', text)
        result_arr = []
        for el in tmp_arr:
            # удаление скобок и разделителя
            tmp = re.split(r'[\[\|\]]', el)
            tmp_arr2 = []
            for e in tmp:
                # убираются пустые строки
                if e != '':
                    tmp_arr2.append(e)
            # ссылки приводятся к MARKDOWN
            result_arr.append(f"[{tmp_arr2[1]}](https://vk.com/{tmp_arr2[0]})")
        # замена ссылок в тексте на ссылки в стиле MARKDOWN
        for i in range(len(tmp_arr)):
            text = text.replace(tmp_arr[i], result_arr[i])
        # происходит экранирование всех специальных знаков MARKDOWN
        text = Format.escape_markdown(text)
        text.replace(" - ", " \- ")
        # разэкранирование ссылкок, так как MARKDOWN не будет читать заэкранированные ссылки
        text = unescape_link(text, result_arr)
        print(text)
        return text
    except:
        print("Произошла ошибка при попытке изменить ссылку")
        return tmp_text


# разэкранирование ссылок
def unescape_link(text: str, link_arr: list):
    for el in link_arr:
        # находим текст незаэкранированной ссылки
        tmp_text_link = re.findall(r'[[]{1}.*?[]]{1}', el)[0]
        tmp_text_link = str(tmp_text_link).replace('[', '')
        tmp_text_link = str(tmp_text_link).replace(']', '')
        # экранируем текст ссылки
        tmp_res_text_link = Format.escape_markdown(tmp_text_link)
        # экранируем ссылку
        tmp = Format.escape_markdown(el)
        # заменяем экранированную ссылку на неэкранированную
        text = text.replace(tmp, el)
        # заменяем неэкранированный текст ссылки на экранированный
        text = text.replace(tmp_text_link, tmp_res_text_link)
    return text


def escape_telegram_entities(text):
    # Экранирование специальных символов в формате разметки Telegram
    text = text.replace('.', r'.')
    return text


def get_vk_hyperlinks_markdown(text):
    text = text.replace('-', ' ')
    # Паттерн для поиска упоминаний пользователей и групп VK
    pattern = r'\[(id\d+|club\d+|https?://vk\.com/[^|]+)\|([^\]]+)\]'
    result_arr_link = []

    # Поиск упоминаний и замена на гиперссылки
    def replace_mention(match):
        entity_id = match.group(1)
        entity_name = match.group(2)
        entity_name = escape_markdown(text=entity_name, version=2)
        if entity_id.startswith('id'):
            result_arr_link.append(f"[{entity_name}](https://vk.com/{entity_id})")
            return f"PLACEHOLDER{len(result_arr_link)}"
        elif entity_id.startswith('club'):
            result_arr_link.append(f"[{entity_name}](https://vk.com/{entity_id})")
            return f"PLACEHOLDER{len(result_arr_link)}"
        else:
            result_arr_link.append(f"[{entity_name}]({entity_id})")
            return f"PLACEHOLDER{len(result_arr_link)}"

    # Замена упоминаний на гиперссылки в формате Markdown V2
    processed_text = re.sub(pattern, replace_mention, text)
    # processed_text = Format.escape_markdown(processed_text)
    processed_text = escape_markdown(text=processed_text, version=2)
    processed_text = escape_telegram_entities(processed_text)

    # Восстановление гиперссылок после экранирования
    for i, link in enumerate(result_arr_link):
        processed_text = processed_text.replace(f"PLACEHOLDER{i + 1}", link)

    return processed_text
