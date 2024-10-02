from pymysql import connect, Error

# Данные для взаимодействия с базой данных
db_host = "mariadb"
db_port = 3306
db_username = "root"
db_userpass = "132432"
db_name = "botdata"


# # Данные для взаимодействия с базой данных
# db_host = "d02c4.mysql.pythonanywhere-services.com"
# db_port = 3306
# db_username = "d02c4"
# db_userpass = "Y$w5c6pU@5&v4v$he$fJzoVbe8PG2"
# db_name = "d02c4$tgdb"


# функция для получения соединения с базой данных
def get_connection():
    connections = None
    try:
        connections = connect(
            host=db_host,
            port=db_port,
            user=db_username,
            passwd=db_userpass,
            database=db_name
        )
        print("ouuuu may")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connections


# функция возвращает ответ на запрос
def answer_on_request(conn, request):
    cursor = conn.cursor()
    result = None
    try:
        cursor.execute(request)
        result = cursor.fetchall()
        conn.commit()
    except Error as e:
        print(f"Ошибка '{e}' обнаружена")
    return result


# # Добавление записи в базу данных
# def add_to_database(connection, group_id, post_link, post_text_id, post_date, array_attachment):
#     try:
#         # добавляем запись в таблицу post
#         request_text = (f"INSERT INTO `post` (`group_id`, `post_link`, `post_text_id`, `post_date`) "
#                         f"VALUES ('{group_id}', '{post_link}', '{post_text_id}', '{post_date}')")
#         answer_on_request(connection, request_text)
#     except:
#         print("Что-то пошло не так")
#     try:
#         # получаем id записи
#         request_text = f"SELECT `post_id` FROM `post` WHERE `post_link` = '{post_link}'"
#         post_id = answer_on_request(connection, request_text)
#         for index in post_id:
#             for ind in index:
#                 for attachment in array_attachment:
#                     try:
#                         # добавление вложений к
#                         if len(attachment[1]) != 0:
#                             request_text = (f"INSERT INTO `attachment` (`post_id`,`attachment_type`, `attachment_link`) "
#                                             f"VALUES ('{ind}','{attachment[0]}','{attachment[1][0]}')")
#                             answer_on_request(connection, request_text)
#                     except:
#                         print("Попытка повторного добавления")
#
#     except:
#         print("Большая ошибка")


def return_source_id_by_link(link: str):
    conn = get_connection()
    request = f"SELECT `source_id` FROM `source` WHERE `source_link` = '{link}';"
    post_arr = answer_on_request(conn, request)
    conn.close()

    return post_arr[0][0]


def return_source_id_by_needed_id(needed_id: int):
    conn = get_connection()
    request = f"SELECT `source_id` FROM `source` WHERE `source_needed_id` = '{needed_id}';"
    post_arr = answer_on_request(conn, request)
    conn.close()
    return post_arr[0][0]


def return_arr_answer(request: str):
    conn = get_connection()
    user_arr = answer_on_request(conn, request)
    conn.close()
    returned_arr = []
    for el in user_arr:
        returned_arr.append(el[0])
    return returned_arr


def add_to_database(connection: connect, source_id, post_link, post_text_id, post_date, array_attachment):
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                # добавляем запись в таблицу post
                request_text = (f"INSERT INTO `post` (`source_id`, `post_link`, `post_text_id`, `post_date`) "
                                f"VALUES ('{source_id}', '{post_link}', '{post_text_id}', '{post_date}')")
                try:
                    cursor.execute(request_text)
                except Error as e:
                    if e.args[0] == 1062:  # Код ошибки для дубликата первичного ключа
                        print(f"Пост с таким post_link уже существует: {post_link}")
                        return
                    else:
                        raise

                # получаем id записи
                request_text = f"SELECT `post_id` FROM `post` WHERE `post_link` = '{post_link}'"
                cursor.execute(request_text)
                post_id = cursor.fetchone()

                for attachment in array_attachment:
                    try:
                        # добавление вложений к
                        if len(attachment[1]) != 0:
                            for att in attachment[1]:
                                request_text = (
                                    f"INSERT INTO `attachment` (`post_id`,`attachment_type`, `attachment_link`) "
                                    f"VALUES ('{post_id[0]}','{attachment[0]}','{att}')")
                                cursor.execute(request_text)
                    except Exception as e:
                        print("Попытка повторного добавления")
                        print(e)

                # Фиксируем транзакцию
                conn.commit()
    except Error as err:
        print(f"Что-то пошло не так: {err}")
        # Откатываем транзакцию в случае ошибки
        conn.rollback()
