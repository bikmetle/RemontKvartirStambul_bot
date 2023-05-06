import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import ChatTypeFilter
from sqlalchemy import func
from config import TOKEN, OWNER, GROUP
from functions import (
    get_user, 
    new_offer_keyboard, 
    published_offer_keyboard, 
    group_keyboard, 
    add_response, 
    id_and_text,
    responses_data,
)
from models import UserModel, OfferModel, ResponseModel, CommentModel, session

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    return await message.answer("В сообщении следует указать:\n - Вид работы\n - Адрес\n - Готов заплатить\n - Дополнительно\nОбратившись к нам мы максимально постараемся вам помочь в вашем деле!")


@dp.message_handler(commands=['chatid'])
async def send_welcome(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"Chat ID is\n{chat_id}")


@dp.message_handler(is_reply=True)
async def edit_offer_handler(message: types.Message):
    """
    This function edit message in owner chat
    """
    replied_message = message.reply_to_message

    # send private message to customer
    if not replied_message.reply_markup:
        try:
            customer_id, text = id_and_text(replied_message.text)
            await bot.send_message(customer_id, text=message.text)
        except:
            try:
                await message.reply(text='Похоже ты ответил не на то сообщение.\nНе доставленно')
            except:
                pass
    # edit offer's discription
    elif message.from_user.id == OWNER and replied_message.chat.id == OWNER:
        offer_id, text = id_and_text(replied_message.text)
        try:
            responses_number = text[text.index('\nОткликнулось: '):]
        except:
            responses_number = ""
        try:
            await bot.edit_message_text(
                text=f"[{offer_id}]\n{message.text}{responses_number}", 
                message_id=replied_message.message_id, 
                chat_id=OWNER, 
                reply_markup=replied_message.reply_markup
            )
            # if offer is published edit message in group as well
            if replied_message.reply_markup.inline_keyboard[0][0]['callback_data'] == 'close':
                await bot.edit_message_text(
                    text=f"[{replied_message.message_id}]\n{message.text}{responses_number}",
                    message_id=offer_id, 
                    chat_id=GROUP, 
                    reply_markup=group_keyboard()
                )
            session.query(OfferModel).filter_by(id=offer_id).update({'description': message.text})
            session.commit()
        except:
            pass
        await message.delete()

private_chat_filter = ChatTypeFilter(types.ChatType.PRIVATE)
@dp.message_handler(private_chat_filter)
async def communication(message: types.Message):
    customer_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    # send customer message to owner so he can edit, publish or delete
    await bot.send_message(OWNER, text=get_user(message), parse_mode="HTML")
    await bot.send_message(OWNER, text="Пока что никто не откликнулся")
    await bot.send_message(OWNER, text=f"[{message.from_id}]\n{message.text}", reply_markup=new_offer_keyboard())
    
    data = {'id': customer_id, 'full_name': full_name, 'username': username}
    obj = UserModel(**data)
    session.merge(obj)
    session.commit()


@dp.callback_query_handler(lambda query: query.data == "publish")
async def process_publish(query: types.CallbackQuery):
    message_id = query.message.message_id
    customer_id, text = id_and_text(query.message.text)
    # reopen closed offer
    try:
        offer_post = await bot.edit_message_text(
            chat_id=GROUP,
            message_id=customer_id, 
            text=f"[{query.message.message_id}]\n{text}", 
            reply_markup=group_keyboard()
        )
        is_new_offer = False
    # send new offer to group
    except:
        offer_post = await bot.send_message(
            chat_id=GROUP, 
            text=f"[{query.message.message_id}]\n{text}", 
            reply_markup=group_keyboard()
        )
        is_new_offer = True
    offer_id = offer_post.message_id
    edited_text = f"[{offer_id}]\n{text}"
    # change publish button to close button
    await bot.edit_message_text(
        text=edited_text, 
        chat_id=OWNER, 
        message_id=message_id, 
        reply_markup=published_offer_keyboard()
    )
    if is_new_offer:

        db_offer = OfferModel(
            id = offer_id,
            customer_id = customer_id,
            description = text,
            date = query.message.date
        )
        session.add(db_offer)
        session.commit()
    await query.answer("Успешно опубилкованно", show_alert=True)


@dp.callback_query_handler(lambda query: query.data == "close")
async def process_close(query: types.CallbackQuery):
    query_text = query.message.text
    offer_id, text = id_and_text(query_text)
    message_id = query.message.message_id
    # remove respond button from offer in group
    await bot.edit_message_text(
        text=f"[{message_id}]\n{text}", 
        chat_id=GROUP, 
        message_id=offer_id
    )
    # change close button to publish button
    await bot.edit_message_text(
        text=query_text, 
        chat_id=OWNER, 
        message_id=message_id, 
        reply_markup=new_offer_keyboard()
    )


@dp.callback_query_handler(lambda query: query.data == "edit")
async def process_edit(query: types.CallbackQuery):
    text = "Сделай свайп на лево по сообщению и напиши свой вариант"
    message = await query.answer(text=text, show_alert=True)


@dp.callback_query_handler(lambda query: query.data == "delete")
async def process_delete(query: types.CallbackQuery):
    message_id = query.message.message_id
    text = query.message.text
    try:
        responses_number = int(text[text.index('\nОткликнулось: ')+15:])
        if responses_number > 0:
            await query.answer("У этого предложения есть отклики. Удали в ручную", show_alert=True)
        elif responses_number == 0:
            await query.message.delete()
            await bot.delete_message(chat_id=OWNER, message_id=message_id-1)
            await bot.delete_message(chat_id=OWNER, message_id=message_id-2)
    except:
        await query.message.delete()
        await bot.delete_message(chat_id=OWNER, message_id=message_id-1)
        await bot.delete_message(chat_id=OWNER, message_id=message_id-2)


@dp.callback_query_handler(lambda query: query.data == "respond")
async def process_respond(query: types.CallbackQuery):
    applicant_id = query.from_user.id
    offer_id = query.message.message_id
    username = query.from_user.username
    full_name = query.from_user.full_name

    data = {'id': applicant_id, 'full_name': full_name, 'username': username}
    obj = UserModel(**data)
    session.merge(obj)
    session.commit()

    obj = session.query(ResponseModel).filter_by(applicant_id=applicant_id, offer_id=offer_id)
    try:
        if obj.first().is_canceled:
            obj.update({'is_canceled': 0})
            session.commit()
            await query.answer("Принято", show_alert=True)
        else:
            obj.update({'is_canceled': 1})
            session.commit()
            await query.answer("Отменено", show_alert=True)
    except:
        db_response = ResponseModel(
            applicant_id=applicant_id,
            offer_id=offer_id
        )
        session.add(db_response)
        session.commit()
        await query.answer("Принято", show_alert=True)

    objs = session.query(UserModel, ResponseModel).outerjoin(ResponseModel).filter_by(offer_id=offer_id, is_canceled=0)
    responses_number = objs.count()
    responses_info = responses_data(objs) if responses_number else "Пока что никто не откликнулся"


    # chage response's number in group message
    text = add_response(query.message.text, responses_number)
    await bot.edit_message_text(
        text=text, 
        message_id=offer_id, 
        chat_id=GROUP, 
        reply_markup=query.message.reply_markup
    )
    # and update owner message
    message_id, text = id_and_text(text)
    await bot.edit_message_text(
        text=responses_info, 
        message_id=message_id-1,
        chat_id=OWNER, 
        parse_mode="HTML"
    )        
    await bot.edit_message_text(
        text=f"[{offer_id}]\n{text}", 
        message_id=message_id,
        chat_id=OWNER, 
        reply_markup=published_offer_keyboard()
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)