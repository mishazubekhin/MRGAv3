import datetime
import sqlite3
import time

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, CallbackQuery, Message, \
    InputMediaPhoto
from pyrogram import Client, filters, enums
import os
from dotenv import load_dotenv
from blocked_word_func import blocked_word, condition_filter, photo_filter_custom, not_media_group, time_date_check, \
    detect_photo
from data_base_users import DB_poll
from date_base_polls import User_polls

load_dotenv()
api_id = os.getenv('ID_TG')
api_hash = os.getenv('HASH_TG')
bot_token = os.getenv('TOKEN_TG')

app = Client("mrga", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
GROUP = 'MakeRussiaGreatAgain_official'

WELCOME_MESSAGE = 'Доступная демократия сейчас!\nЧтобы начать делать жизнь лучше нажмите /start'
WELCOME_MESSAGE_AFTER_START = '''
 Вы стали активным участником в жизни общества!\n
 Вам будут приходить голосования, запущенные такими же, как ты!\n 
 Для начала выберите свой регион, нажав на кнопку "Выбрать свой дом"\n
 Чтобы создать голосование в выбранном регионе, нажмите кнопку "Создать голосование"\n
 Чтобы вызвать свои последние три голосования, нажмите кнопку "Мои петиции"\n
 Чтобы понять, ЧТО ВООБЩЕ ПРОИСХОДИТ, нажмите кнопку "Инструкция" '''

WELCOME_MESSAGE_BUTTONS = [
    [InlineKeyboardButton('Выбрать свой дом', callback_data='choose_home')],
    [InlineKeyboardButton('Создать голосование', callback_data='create_universal_vote')],
    [InlineKeyboardButton('Мои петиции', callback_data='my_petition')],
    [InlineKeyboardButton('Инструкция на нашем канале', url='https://t.me/MakeRussiaGreatAgain_official/19')]
]


@app.on_message(filters.command('start'))
async def welcome_start(app: Client, message: Message):
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute(f"UPDATE polls SET condition = ('start') WHERE user_id = ('{message.from_user.id}');")
    db_vote.commit()
    cur_vote.execute(f"INSERT OR IGNORE INTO polls (user_id) VALUES ('{message.from_user.id}')")
    db_vote.commit()
    db_vote.close()
    reply_markup = InlineKeyboardMarkup(WELCOME_MESSAGE_BUTTONS)
    await message.reply(text=WELCOME_MESSAGE_AFTER_START, reply_markup=reply_markup, disable_web_page_preview=True)
    return


region_list = []
with open('list_region_car.txt', encoding='utf-8') as file:
    for region in file:
        region = region.replace('\n', '')
        region_list.append(region)


@app.on_callback_query(group=3)
async def home(app: Client, answer_message: CallbackQuery):
    if answer_message.data == 'home':
        db_poll = DB_poll()
        db_poll.update_condition(stream="start", user_id=answer_message.from_user.id)
        await answer_message.edit_message_text(text=WELCOME_MESSAGE_AFTER_START,
                                               reply_markup=InlineKeyboardMarkup(WELCOME_MESSAGE_BUTTONS),
                                               disable_web_page_preview=True)
        return
    return


@app.on_callback_query(condition_filter(['start']), group=1)
async def create_vote(app: Client, answer_message: CallbackQuery):
    if answer_message.data == 'my_petition':
        user_polls = User_polls()
        poll_and_photo = user_polls.return_poll(answer_message.from_user.id)
        poll_list = poll_and_photo[0]
        photo_list = poll_and_photo[1]
        if user_polls.return_user_id(answer_message.from_user.id):
            await app.send_message(answer_message.from_user.id, "У вас нет петиций!🙄")
        else:
            for (i, n) in zip(poll_list, photo_list):
                if n != "None":
                    await app.send_photo(answer_message.from_user.id, photo=n)
                await app.forward_messages(answer_message.from_user.id, answer_message.from_user.id,
                                           message_ids=i)
                time.sleep(3)
        return
    if answer_message.data == 'create_universal_vote':
        db_poll = DB_poll()
        if db_poll.check_date(user_id=answer_message.from_user.id) == datetime.datetime.now().strftime("%Y%m%d"):
            await app.send_message(chat_id=answer_message.from_user.id,
                                   text="Вы можете создавать петиции не чаще одного раза в сутки",
                                   disable_web_page_preview=True)
        else:
            db_poll.update_condition(stream="command_poll", user_id=answer_message.from_user.id)
            CREATE_POLL_MESSAGE = 'Изложите, пожалуйста, в сообщении ⬇️⬇️⬇️ проблему, согласно инструкции'
            reply_markup_tutorial = [
                [InlineKeyboardButton('Инструкция', url='https://t.me/MakeRussiaGreatAgain_official/19')],
                [InlineKeyboardButton('Вернуться на главную', callback_data='home')]
            ]
            await app.send_message(chat_id=answer_message.from_user.id, text=CREATE_POLL_MESSAGE,
                                   reply_markup=InlineKeyboardMarkup(reply_markup_tutorial),
                                   disable_web_page_preview=True)

        return
    if answer_message.data == 'choose_home':
        db_poll = DB_poll()
        db_poll.update_condition(stream="choose_home", user_id=answer_message.from_user.id)
        MESSAGE_CHOOSE_REGION = 'Введите номер вашего региона!\nДля уточнения номера Вашего региона, нажмите кнопку ' \
                                '"Список регионов"'
        reply_choose_region = [
            [InlineKeyboardButton('Список регионов', url='https://www.consultant.ru/document/cons_doc_LAW_108669'
                                                         '/88a12659e7cc781c56303430d98ae6c8a683892a/')],
            [InlineKeyboardButton('Вернуться на главную страницу', callback_data='home')]
        ]
        await app.send_message(text=MESSAGE_CHOOSE_REGION, chat_id=answer_message.from_user.id,
                               reply_markup=InlineKeyboardMarkup(reply_choose_region))

        @app.on_message(condition_filter(["choose_home"]), group=1)
        async def choose_region(app: Client, message: Message):
            if message.text in region_list:
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set region = ('{message.text}') WHERE user_id = ('{message.from_user.id}')")
                db_vote.commit()
                cur_vote.execute(f"UPDATE polls SET condition = ('start') WHERE user_id = ('{message.from_user.id}');")
                db_vote.commit()
                db_vote.close()
                go_home = [
                    [InlineKeyboardButton('Вернуться на главную страницу', callback_data='home')],
                    [InlineKeyboardButton('Сменить регион', callback_data='choose_home')]
                ]
                await app.send_message(chat_id=message.from_user.id,
                                       text='Прекрасно!\nТеперь ты сможешь участвовать в голосованиях своего региона!',
                                       reply_markup=InlineKeyboardMarkup(go_home))
                return
            else:
                await app.send_message(chat_id=message.from_user.id, text='Нет такого региона!',
                                       reply_markup=InlineKeyboardMarkup(reply_choose_region))
                return

        return
    return


@app.on_message(filters.text & condition_filter(["command_poll"]), group=2)
async def poll_creating(app: Client, message: Message):
    db_poll = DB_poll()
    if db_poll.simple_condition(message.from_user.id) != 'null':
        if time_date_check(message.from_user.id):
            if await blocked_word(app, message) is False:
                input_message = message.text
                msg_poll = await app.send_poll(chat_id=message.from_user.id, is_anonymous=False,
                                               question=input_message,
                                               options=['Согласен', "Возражаю",
                                                        "Не могу объективно оценить проблему"])
                msg_poll_id = msg_poll.id
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set photos = (Null),"
                    f"second_photo = (Null),"
                    f"third_photo = (Null),"
                    f"forth_photo = (Null),"
                    f"fiveth_photo = (Null),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{message.from_user.id}')")
                cur_vote.execute(
                    f"UPDATE polls SET condition = ('check_create') WHERE user_id = ('{message.from_user.id}');")
                cur_vote.execute(
                    f"UPDATE polls set poll_id = ('{msg_poll_id}') WHERE user_id = ('{message.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                CHECK_FOR_CORRECT = 'Проверьте, верно ли все, что вы хотели изложить?!\nДобавьте подтверждающие ' \
                                    'фотографии\nЕсли что-то неверно, продублируйте весь текст с учетом правок, ' \
                                    'нажав на кнопку "Хочу немного исправить!"'
                CHECK_CORRECT_BUTTONS = [
                    [InlineKeyboardButton('Добавить фотографии к петиции', callback_data='add_photo')],
                    [InlineKeyboardButton('Опубликовать без фотографий', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить!', callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]
                ]
                reply_markup_1 = InlineKeyboardMarkup(CHECK_CORRECT_BUTTONS)
                await app.send_message(chat_id=message.from_user.id, text=CHECK_FOR_CORRECT,
                                       reply_markup=reply_markup_1)

            else:
                CREATE_POLL_MESSAGE = 'Изложите, пожалуйста, в сообщении ⬇️⬇️⬇️ проблему, согласно инструкции'
                reply_markup_tutorial = [
                    [InlineKeyboardButton('Инструкция', url='https://t.me/MakeRussiaGreatAgain_official/19')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]
                ]
                await app.send_message(chat_id=message.from_user.id, text=CREATE_POLL_MESSAGE,
                                       reply_markup=InlineKeyboardMarkup(reply_markup_tutorial),
                                       disable_web_page_preview=True)
                return
        else:
            await app.send_message(chat_id=message.from_user.id,
                                   text="Вы можете создавать петиции не чаще одного раза в сутки!"
                                        "Подготовьтесь пока получше!",
                                   disable_web_page_preview=True)
        return
    else:
        await app.send_message(chat_id=message.from_user.id,
                                   text="Для начала выберите, пожалуйста, свой регион!",
                                   disable_web_page_preview=True)


@app.on_callback_query(condition_filter(['check_create', 'add_first_photo', 'add_second_photo', 'add_third_photo',
                                         'add_forth_photo', 'add_fiveth_photo', 'add_sixth_photo',
                                         'add_seventh_photo']), group=2)
def improve_vote(app: Client, answer_message: CallbackQuery):
    if answer_message.data == 'all_right':
        app.send_chat_action(answer_message.from_user.id, enums.ChatAction.IMPORT_HISTORY)
        db_poll = DB_poll()
        message_poll_id = db_poll.return_poll_id(user_id=answer_message.from_user.id)
        message_photo_id = db_poll.return_photos(answer_message.from_user.id)
        db_poll.update_date(user_id=answer_message.from_user.id)
        user_polls = User_polls()
        user_polls.add_poll(user_id=answer_message.from_user.id, poll_id=message_poll_id,
                            photo=message_photo_id)
        enum_user_id = db_poll.return_user_id(user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('На главную', callback_data='home')],
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        if db_poll.simple_condition(answer_message.from_user.id) == "check_create":
            db_poll.update_condition('start', answer_message.from_user.id)
            for id_user in enum_user_id:
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=message_poll_id)
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_first_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            for id_user in enum_user_id:
                app.send_photo(id_user, photo=message_photo_id, protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_second_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id))
                                ]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_third_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_third_photo(answer_message.from_user.id))
                                ]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_forth_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_third_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_forth_photo(answer_message.from_user.id))
                                ]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_fiveth_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_third_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_forth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_fiveth_photo(answer_message.from_user.id)),
                                ]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_sixth_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_third_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_forth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_fiveth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_sixth_photo(answer_message.from_user.id)),
                                ]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
        if db_poll.simple_condition(answer_message.from_user.id) == "add_seventh_photo":
            db_poll.update_condition('start', answer_message.from_user.id)
            list_photo_users = [InputMediaPhoto(db_poll.return_photos(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_second_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_third_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_forth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_fiveth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_sixth_photo(answer_message.from_user.id)),
                                InputMediaPhoto(db_poll.return_seventh_photo(answer_message.from_user.id))]
            for id_user in enum_user_id:
                app.send_media_group(id_user, media=list_photo_users,
                                     protect_content=True)
                app.forward_messages(id_user, answer_message.from_user.id,
                                     message_ids=db_poll.return_poll_id(
                                         user_id=answer_message.from_user.id))
            app.send_message(answer_message.from_user.id, 'Ваше голосование опубликовано!',
                             reply_markup=reply_markup_back_home,
                             disable_web_page_preview=True)
            return
    elif answer_message.data == 'add_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_first_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Назад', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Добавьте первую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_first_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.from_user.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set photos = ('{photo.photo.file_id}'),"
                    f"second_photo = (Null),"
                    f"third_photo = (Null),"
                    f"forth_photo = (Null),"
                    f"fiveth_photo = (Null),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить вторую фотографию!', callback_data='add_second_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_photo(photo.from_user.id, return_photo)
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Одной фотографии всегда мало..",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id,
                                       "Наш искусственный интеллект еще в процессе обучения, но сейчас он "
                                       "заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_second_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_second_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте следующую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_second_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set second_photo = ('{photo.photo.file_id}'),"
                    f"third_photo = (Null),"
                    f"forth_photo = (Null),"
                    f"fiveth_photo = (Null),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить третью фотографию!', callback_data='add_third_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second)])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит неплохо!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_third_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_third_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте следующую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_third_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set third_photo = ('{photo.photo.file_id}'),"
                    f"forth_photo = (Null),"
                    f"fiveth_photo = (Null),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                return_third = db_poll.return_third_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить четвертую фотографию!',
                                          callback_data='add_forth_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second),
                    InputMediaPhoto(return_third)])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит супер!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_forth_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_forth_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте следующую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_forth_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set forth_photo = ('{photo.photo.file_id}'),"
                    f"fiveth_photo = (Null),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                return_third = db_poll.return_third_photo(user_id=photo.from_user.id)
                return_forth = db_poll.return_forth_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить пятую фотографию!', callback_data='add_fiveth_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second),
                    InputMediaPhoto(return_third),
                    InputMediaPhoto(return_forth)])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит прекрасно!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_fiveth_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_fiveth_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте пятую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_fiveth_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set fiveth_photo = ('{photo.photo.file_id}'),"
                    f"sixth_photo = (Null),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                return_third = db_poll.return_third_photo(user_id=photo.from_user.id)
                return_forth = db_poll.return_forth_photo(user_id=photo.from_user.id)
                return_fiveth = db_poll.return_fiveth_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить шестую фотографию!', callback_data='add_sixth_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second),
                    InputMediaPhoto(return_third),
                    InputMediaPhoto(return_forth),
                    InputMediaPhoto(return_fiveth)])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит ясно и понятно!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_sixth_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_sixth_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте шестую фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_sixth_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set sixth_photo = ('{photo.photo.file_id}'),"
                    f"seventh_photo = (Null)"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                return_third = db_poll.return_third_photo(user_id=photo.from_user.id)
                return_forth = db_poll.return_forth_photo(user_id=photo.from_user.id)
                return_fiveth = db_poll.return_fiveth_photo(user_id=photo.from_user.id)
                return_sixth = db_poll.return_sixth_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Добавить последнюю фотографию!',
                                          callback_data='add_seventh_photo')],
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second),
                    InputMediaPhoto(return_third),
                    InputMediaPhoto(return_forth),
                    InputMediaPhoto(return_fiveth),
                    InputMediaPhoto(return_sixth)
                ])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит, как очень важное!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'add_seventh_photo':
        db_poll = DB_poll()
        db_poll.update_condition(stream="add_seventh_photo", user_id=answer_message.from_user.id)
        ADD_PHOTO = [
            [InlineKeyboardButton('Начать с начала', callback_data='make_edit')],
            [InlineKeyboardButton('На главную', callback_data='home')]
        ]
        reply_markup_back_home = InlineKeyboardMarkup(ADD_PHOTO)
        app.send_message(answer_message.from_user.id, 'Отправьте последнюю фотографию!',
                         reply_markup=reply_markup_back_home,
                         disable_web_page_preview=True)

        @app.on_message(filters.photo & condition_filter(["add_seventh_photo"]) & not_media_group())
        async def save_photos(app: Client, photo: Message):
            await app.send_chat_action(photo.chat.id, enums.ChatAction.UPLOAD_PHOTO)
            if photo_filter_custom(photo) is True:
                time.sleep(2)
                db_vote = sqlite3.connect("tguser.db")
                cur_vote = db_vote.cursor()
                cur_vote.execute(
                    f"UPDATE polls set seventh_photo = ('{photo.photo.file_id}')"
                    f"WHERE user_id = ('{photo.from_user.id}')")
                db_vote.commit()
                db_vote.close()
                await app.delete_messages(chat_id=photo.from_user.id, message_ids=photo.id)
                db_poll = DB_poll()
                return_photo = db_poll.return_photos(user_id=photo.from_user.id)
                return_second = db_poll.return_second_photo(user_id=photo.from_user.id)
                return_third = db_poll.return_third_photo(user_id=photo.from_user.id)
                return_forth = db_poll.return_forth_photo(user_id=photo.from_user.id)
                return_fiveth = db_poll.return_fiveth_photo(user_id=photo.from_user.id)
                return_sixth = db_poll.return_sixth_photo(user_id=photo.from_user.id)
                return_seventh = db_poll.return_seventh_photo(user_id=photo.from_user.id)
                CHECK_CORRECT_PHOTOS = [
                    [InlineKeyboardButton('Все готово! Опубликовать!', callback_data='all_right')],
                    [InlineKeyboardButton('Хочу исправить текст и поменять фотографии!',
                                          callback_data='make_edit')],
                    [InlineKeyboardButton('Вернуться на главную', callback_data='home')]]
                await app.send_media_group(photo.from_user.id, [
                    InputMediaPhoto(return_photo),
                    InputMediaPhoto(return_second),
                    InputMediaPhoto(return_third),
                    InputMediaPhoto(return_forth),
                    InputMediaPhoto(return_fiveth),
                    InputMediaPhoto(return_sixth),
                    InputMediaPhoto(return_seventh)
                ])
                await app.forward_messages(photo.from_user.id, photo.from_user.id,
                                           db_poll.return_poll_id(user_id=photo.from_user.id))
                await app.send_message(photo.from_user.id, "Выглядит максимально наполненно и ясно!",
                                       reply_markup=InlineKeyboardMarkup(CHECK_CORRECT_PHOTOS))
            else:
                time.sleep(2)
                await app.send_message(photo.from_user.id, "Наш искусственный интеллект еще в процессе обучения, "
                                                           "но сейчас он заблокировал Вашу фотографию🙊")

        return
    elif answer_message.data == 'make_edit':
        db_poll = DB_poll()
        db_poll.update_condition(stream="command_poll", user_id=answer_message.from_user.id)
        app.send_message(chat_id=answer_message.from_user.id, text='Введите заново полностью текст '
                                                                   'Вашей проблемы, с учетом правок!')
        return
    return


@app.on_message(filters.new_chat_members)
async def welcome_group(app: Client, message: Message):
    time = datetime.datetime.now() - datetime.timedelta(days=1)
    time = time.strftime("%Y%m%d")
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute(f"INSERT OR IGNORE INTO polls (user_id) VALUES ('{message.from_user.id}')")
    db_vote.commit()
    cur_vote.execute(f"UPDATE polls SET check_time = ('{time}') WHERE user_id = ('{message.from_user.id}');")
    db_vote.commit()
    db_vote.close()
    reply_buttons = [
        ['/start']
    ]
    reply_keyboard = ReplyKeyboardMarkup(reply_buttons, one_time_keyboard=True, resize_keyboard=True)
    await message.reply_text(WELCOME_MESSAGE, reply_markup=reply_keyboard)
    await app.send_photo(message.chat.id,
                         'AgACAgIAAxkDAAKw3WPfpy7a5YEsMRzQiOXsc6drUyq7AALIxjEbuNIBS3f-tVfPSM5uAAgBAAMCAANtAAceBA')


# блок получения айди файлов
# @app.on_message(filters.audio & filters.private)
# async def get_id_audio(app: Client, message: Message):
#     await message.reply(message.audio.file_id)
#
#
# @app.on_message(filters.photo & filters.me, group=1)
# async def get_id_photo(app: Client, message: Message):
#     await message.reply(message.photo.file_id)



print('I`m working')
app.run()
