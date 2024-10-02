from typing import List

from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import IntegrityError


class Source(Model):
    source_id = fields.IntField(pk=True)
    source_link = fields.CharField(max_length=500, unique=True)
    source_name = fields.CharField(max_length=100, null=True)
    source_needed_id = fields.BigIntField(null=True)
    source_date_update = fields.DatetimeField(auto_now=True)


class User(Model):
    user_id = fields.BigIntField(pk=True)
    user_name = fields.TextField()


class Right(Model):
    right_id = fields.IntField(pk=True)
    right_name = fields.CharField(max_length=50, null=False)

    class Meta:
        table = 'right'
        unique_together = (("right_name",),)


class Group(Model):
    group_id = fields.BigIntField(pk=True)
    group_name = fields.CharField(max_length=50, null=True)
    group_course = fields.IntField()
    right = fields.ForeignKeyField('models.Right', related_name='group')

    class Meta:
        table = 'group'
        unique_together = (("group_name", "group_course", "right"),)


class UserMembership(Model):
    user_membership_id = fields.BigIntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='memberships')
    source = fields.ForeignKeyField('models.Source', related_name='memberships')

    class Meta:
        table = 'user_membership'
        unique_together = (("user", "source"),)


class UserGroup(Model):
    user_group_id = fields.BigIntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='user_group')
    group = fields.ForeignKeyField('models.Group', related_name='user_group')

    class Meta:
        table = 'user_group'
        unique_together = (("user", "group"),)


async def get_all_sources():
    all_sources = await Source.all().values('source_id', 'source_name')
    return all_sources


async def get_all_groups():
    all_group = await Group.all().values('group_id', 'group_name')
    return all_group


async def get_all_groups_student():
    student_groups = await Group.filter(right__right_name="student").values('group_id', 'group_name')
    return student_groups


async def get_source_for_user(user_id):
    user_memberships = await UserMembership.filter(user_id=user_id).prefetch_related('source')
    sources = [{'source_id': membership.source.source_id, 'source_name': membership.source.source_name} for membership
               in
               user_memberships]
    return sources


async def get_groups_student_for_user(user_id):
    # Perform a join between UserGroup and Group models and filter by right_name
    student_groups = await UserGroup.filter(user_id=user_id, group__right__right_name="student").prefetch_related(
        'group')
    groups = [{'group_id': user_group.group.group_id, 'group_name': user_group.group.group_name} for user_group in
              student_groups]
    return groups


async def add_user_membership(user_id, source_id):
    try:
        await UserMembership.create(user_id=user_id, source_id=source_id)
        return True  # Успешно создано
    except Exception as e:
        print(f"Ошибка при создании записи в user_membership: {e}")
        return False  # Возникла ошибка при создании записи


async def add_user_group(user_id, group_id):
    try:
        await UserGroup.create(user_id=user_id, group_id=group_id)
        return True  # Успешно создано
    except Exception as e:
        print(f"Ошибка при создании записи в user_membership: {e}")
        return False  # Возникла ошибка при создании записи


async def remove_user_membership(user_id, source_id):
    try:
        # Находим запись для удаления
        membership = await UserMembership.filter(user_id=user_id, source_id=source_id).first()
        if membership:
            # Если запись найдена, удаляем её
            await membership.delete()
            return True  # Успешно удалено
        else:
            # Если запись не найдена, возвращаем False
            return False  # Запись не найдена
    except Exception as e:
        print(f"Ошибка при удалении записи из user_madd_user_membershipembership: {e}")
        return False  # Возникла ошибка при удалении записи


async def remove_user_group(user_id, group_id):
    try:
        # Находим запись для удаления
        group = await UserGroup.filter(user_id=user_id, group_id=group_id).first()
        if group:
            # Если запись найдена, удаляем её
            await group.delete()
            return True  # Успешно удалено
        else:
            # Если запись не найдена, возвращаем False
            return False  # Запись не найдена
    except Exception as e:
        print(f"Ошибка при удалении записи из user_madd_user_membershipembership: {e}")
        return False  # Возникла ошибка при удалении записи


# Функции для добавления и удаления пользователя из базы данных
async def add_user(user_id, user_name) -> bool:
    # Проверка наличия пользователя в базе данных
    existing_user = await User.get_or_none(user_id=user_id)
    if existing_user:
        # Пользователь уже существует в базе данных
        return False
    else:
        # Добавление нового пользователя в базу данных
        try:
            await User.create(user_id=user_id, user_name=user_name)
            return True
        except IntegrityError:
            # Обработка ошибки уникальности ключа
            return False


async def get_users_in_group(group_id):
    # Filter UserGroup model by group_id and prefetch related User objects
    group_users = await UserGroup.filter(group_id=group_id).prefetch_related('user')

    # Extract user information from the prefetched objects
    users = [{'user_id': group_user.user.user_id, 'user_name': group_user.user.user_name} for group_user in group_users]

    return users


async def get_users_in_groups(group_ids):
    # Filter UserGroup model by group_ids and prefetch related User objects
    group_users = await UserGroup.filter(group_id__in=group_ids).prefetch_related('user')

    # Extract user information from the prefetched objects
    users = [{'user_id': group_user.user.user_id, 'user_name': group_user.user.user_name} for group_user in group_users]

    # Ensure uniqueness by converting list of dictionaries to a set of tuples and back to a list of dictionaries
    unique_users = [dict(t) for t in {tuple(d.items()) for d in users}]

    return unique_users


async def get_unique_courses():
    unique_courses = set(await Group.all().values_list('group_course', flat=True))
    return unique_courses


async def get_unique_group_ids_by_courses(courses):
    unique_group_ids = set()
    for course in courses:
        group_ids = await Group.filter(group_course=course).values_list('group_id', flat=True)
        unique_group_ids.update(group_ids)
    return unique_group_ids


async def get_admin_user_ids():
    admin_user_groups = await UserGroup.filter(group__right__right_name='admin').values_list('user_id', flat=True)

    admin_user_ids = list(admin_user_groups)

    return admin_user_ids


async def get_teacher_user_ids():
    admin_user_groups = await UserGroup.filter(group__right__right_name='teacher').values_list('user_id', flat=True)

    admin_user_ids = list(admin_user_groups)

    return admin_user_ids


from tortoise.exceptions import IntegrityError


async def add_vk_source(group_info: list) -> int:
    try:
        if group_info[2] == 0:
            print('Группы не существует')
            return 0
        else:
            group_id = group_info[1]
            group_name = group_info[3]
            lnk = f"https://vk.com/club{group_id}"
            source = await Source.create(
                source_needed_id=group_id,
                source_name=group_name,
                source_link=lnk
            )
            if source:
                return 1
            else:
                return 0
    except IntegrityError:
        print("Неудачная попытка добавления: Источник уже существует")
        return 0
    except Exception as e:
        print(f"Неудачная попытка добавления: {e}")
        return 0


async def delete_vk_source(group_id: int) -> int:
    try:
        source = await Source.filter(source_needed_id=group_id).first()

        if source:
            await source.delete()
            return 1
        else:
            print(f"Источник с ID {group_id} не найден")
            return 0
    except Exception as e:
        print(f"Ошибка при удалении источника: {e}")
        return 0


async def add_users_to_teacher_group(user_ids: list[int]) -> int:
    try:
        group = await Group.filter(right__right_name='teacher').first()

        if group:
            for user_id in user_ids:
                exists = await UserGroup.filter(user_id=user_id, group_id=group.group_id).exists()
                if not exists:
                    await UserGroup.create(user_id=user_id, group_id=group.group_id)
            return 1
        else:
            print("Группа с правами 'teacher' не найдена")
            return 0
    except Exception as e:
        print(f"Ошибка при добавлении пользователей в группу: {e}")
        return 0


async def add_teacher_to_group(user_id: int) -> int:
    try:
        group = await Group.filter(right__right_name='teacher').first()
        if group:
            exists = await UserGroup.filter(user_id=user_id, group_id=group.group_id).exists()
            if not exists:
                await UserGroup.create(user_id=user_id, group_id=group.group_id)
                return 1
            else:
                print("Пользователь уже состоит в группе с правами 'teacher'")
                return 0
        else:
            print("Группа с правами 'teacher' не найдена")
            return 0
    except Exception as e:
        print(f"Ошибка при добавлении преподавателя в группу: {e}")
        return 0


async def remove_teacher_from_all_groups(user_id: int) -> int:
    try:
        groups = await Group.filter(right__right_name='teacher').all()
        for group in groups:
            exists = await UserGroup.filter(user_id=user_id, group_id=group.group_id).exists()
            if exists:
                await UserGroup.filter(user_id=user_id, group_id=group.group_id).delete()
        return 1
    except Exception as e:
        print(f"Ошибка при удалении преподавателя из групп: {e}")
        return 0


async def delete_user(user_id: int) -> int:
    try:
        user = await User.filter(user_id=user_id).first()
        if user:
            await user.delete()
            return 1
        else:
            print(f"Пользователь с ID {user_id} не найден")
            return 0
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
        return 0
