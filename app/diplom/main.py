def escape_reserved_characters(text):
    return text.replace('|', ' ')


print(escape_reserved_characters("asdfasdf|dsfsdfdf|dsfsdfdsfds|dsfsdfsdf|"))