import datetime
import sqlite3
import requests
import tensorflow as tf
import numpy as np

from pyrogram.types import Message
from pyrogram import Client, filters
import os
from dotenv import load_dotenv
from data_base_users import DB_poll


load_dotenv()

api_id = os.getenv('ID_TG')
api_hash = os.getenv('HASH_TG')
bot_token = os.getenv('TOKEN_TG')

app = Client("mrga", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
GROUP = 'MakeRussiaGreatAgain_official'

# Блок запрещенных слов и ответ на любое сообщение
async def blocked_word(app: Client, message: Message):
    word_black_list = []
    with open('blacklist.txt', encoding='utf-8') as f:
        for word in f:
            word = word.replace('\n', '')
            word_black_list.append(word)
    for dword in word_black_list:
        if message.text.lower().find(dword) != -1:
            await app.delete_messages(message.chat.id, message.id)
            await app.send_message(message.chat.id, 'Присутствуют запрещенные слова!')
            await app.send_photo(message.chat.id,
                           "AgACAgIAAxkBAAPEY-F5nFLZxbtlK-skV19_uqGqLnUAAkXIMRt3VBFLilZPp1oXBlsACAEAAwIAA20ABx4E")
            return
    return False


# создаем фильтры контроля пользователя
def condition_filter(condition_check):
    async def condition_some(_, __, message) -> bool:
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT condition FROM polls WHERE user_id = '{message.from_user.id}';")
        condition_now = cur_vote.fetchone()
        db_vote.close()
        condition_now_str = "".join(condition_now)
        print(condition_now_str)
        print(condition_check)
        print(condition_now_str in condition_check)
        return condition_now_str in condition_check
    return filters.create(condition_some)

# Фильтр плохих фотографий
def detect_photo(photo):
    abs_path = os.path.abspath('/app/detector_photo/Flickr8k_text/Models/my_model.h5')
    model = tf.keras.models.load_model(abs_path)
    file_id = photo.photo.file_id
    url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
    file_path = requests.get(url).json()["result"]["file_path"]
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    data_dir = tf.keras.utils.get_file(origin=download_url)
    input_image = tf.keras.utils.load_img(data_dir)

    class_names = ['bad', 'good']

    img_resized = tf.image.resize(input_image, [224, 224])
    img_expended = np.expand_dims(img_resized, axis=0)
    prediction = model.predict(img_expended)
    print(f'Вероятность отнесения изображения к хорошему: {prediction[0][0] * 10000}%')
    if 0.4 <= prediction[0][0] * 100:
        return class_names[1]
    else:
        return class_names[0]
    # for i, logits in enumerate(prediction):
    #     class_idx = tf.argmax(logits).numpy()
    #     p = tf.sigmoid(logits)[class_idx]
    #     name = class_names[class_idx]
    #     print("Example {} prediction: {} ({:2.1f}%)".format(i, name, 100 * p))
    #     return name

def photo_filter_custom(photo) -> bool:
    return str(detect_photo(photo)) == "good"


def time_date_check(user_id) -> bool:
    db_poll = DB_poll()
    user_date = int(db_poll.check_date(user_id))
    now_date = int(datetime.datetime.now().strftime("%Y%m%d"))
    # time_check = time_date + datetime.timedelta(seconds=100)
    g = now_date > user_date
    print(g)
    return now_date > user_date

def not_media_group():
    async def check_media(_, __, message: Message) -> bool:
        gm = bool(message.media_group_id == None)
        print(gm)
        return gm
    return filters.create(check_media)



