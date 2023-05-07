from aiogram import types


def get_user(message: types.Message):
    """
    This function gets user as a link.
    """
    id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    if message.from_user.username is not None:
        user_link = f"[{id}]\nСообщение от <a href='tg://user?id={id}'>@{username}</a>\n"
    else:
        user_link = f"[{id}]\nСообщение от <a href='tg://user?id={id}'>{full_name}</a>\n"
    return user_link

def new_offer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    publish = types.InlineKeyboardButton(
        text="Опубликовать",
        callback_data="publish"
    )
    edit = types.InlineKeyboardButton(
        text="Редактировать",
        callback_data="edit"
    )
    delete = types.InlineKeyboardButton(
        text="Удалить",
        callback_data="delete"
    )
    close = types.InlineKeyboardButton(
        text="Закрыть",
        callback_data="close"
    )
    keyboard.insert(publish)
    keyboard.insert(edit)
    keyboard.insert(delete)
    return keyboard

def published_offer_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    close = types.InlineKeyboardButton(
        text="Закрыть",
        callback_data="close"
    )
    edit = types.InlineKeyboardButton(
        text="Редактировать",
        callback_data="edit"
    )
    keyboard.insert(close)
    keyboard.insert(edit)
    return keyboard

def group_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    respond = types.InlineKeyboardButton(
        text="откликнуться",
        callback_data="respond"
    )
    keyboard.insert(respond)
    return keyboard

def add_response(text, responses_number):
    if text.split()[-2] == 'Откликнулось:':
        return text[:text.index('Откликнулось: ') + 14] + str(responses_number)
    else:
        text += f'\nОткликнулось: {responses_number}'
    return text

def id_and_text(text):
    id = int(text[text.index('[') + 1:text.index(']\n')])
    text = text[text.index(']\n') + 2:]
    return id, text

def user_link(obj):
    if obj.username:
        text = f"<a href='tg://user?id={obj.id}'>{obj.full_name}</a> @{obj.username}"
    else:
        text = f"<a href='tg://user?id={obj.id}'>{obj.full_name}</a>"
    return text

def responses_data(objs):
    responses = []
    for obj in objs:
        responses.append(f"{user_link(obj[0])}\n")
    return ''.join(responses)

def new_media_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    publish = types.InlineKeyboardButton(
        text="Отправить в группу",
        callback_data="media_publish"
    )
    keyboard.insert(publish)
    return keyboard

def published_media_keyboard(message_id):
    keyboard = types.InlineKeyboardMarkup()
    publish = types.InlineKeyboardButton(
        text="Удалить из группы",
        callback_data=f"media_delete {message_id}"
    )
    keyboard.insert(publish)
    return keyboard
