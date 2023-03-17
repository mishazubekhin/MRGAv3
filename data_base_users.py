import datetime
import sqlite3


# Добавление столбцов
# db_vote = sqlite3.connect("tguser.db")
# cur_vote = db_vote.cursor()
# cur_vote.execute("""ALTER TABLE polls ADD COLUMN check_time TEXT""")
# db_vote.commit()


class DB_poll(object):
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute("""CREATE TABLE IF NOT EXISTS polls (
        user_id INT PRIMARY KEY,
        poll_id INTEGER,
        photos BLOB,
        region TEXT,
        condition TEXT DEFAULT 'start',
        second_photo BLOB,
        third_photo BLOB,
        forth_photo BLOB, 
        fiveth_photo BLOB,
        sixth_photo BLOB,
        seventh_photo BLOB,
        check_time TEXT DEFAULT '1');
        """)
    db_vote.commit()
    db_vote.close()

    def return_user_id(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT region FROM polls WHERE user_id = '{user_id}'; ")
        region_user = cur_vote.fetchone()
        region_user = region_user[0]
        cur_vote.execute(f"SELECT user_id FROM polls WHERE region = '{region_user}'")
        user_id_all = cur_vote.fetchall()
        db_vote.close()
        user_id_all_list = []
        for i in user_id_all:
            user_id_all_list.append(i[0])
        return user_id_all_list

    def return_poll_id(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT poll_id FROM polls WHERE user_id = '{user_id}';")
        poll_id_own = cur_vote.fetchone()
        db_vote.close()
        poll_id_own_list = poll_id_own[0]
        return poll_id_own_list

    # блок обработчиков фотографий
    def return_photos(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT photos FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_second_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT second_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_third_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT third_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_forth_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT forth_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_fiveth_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT fiveth_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_sixth_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT sixth_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    def return_seventh_photo(self, user_id: int):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT seventh_photo FROM polls WHERE user_id = '{user_id}';")
        photos_id_own = cur_vote.fetchone()
        db_vote.close()
        photos_own_list = photos_id_own[0]
        return photos_own_list

    # Функция обновления состояния пользователя

    def update_condition(self, stream, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"UPDATE polls SET condition = ('{stream}') WHERE user_id = ('{user_id}');")
        db_vote.commit()
        db_vote.close()
        return

    def simple_condition(self, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT condition FROM polls WHERE user_id = '{user_id}';")
        condition_own = cur_vote.fetchone()
        db_vote.close()
        condition_list = ''.join(condition_own)
        print(condition_list)
        return condition_list

    def simple_region(self, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT region FROM polls WHERE user_id = '{user_id}';")
        region_own = cur_vote.fetchone()
        db_vote.close()
        region_list = region_own[0]
        return region_list

    def update_date(self, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f'''UPDATE polls SET check_time = ('{datetime.datetime.now().strftime("%Y%m%d")}') WHERE user_id = '{user_id}';''')
        db_vote.commit()
        db_vote.close()
        return

    def check_date(self, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT check_time FROM polls WHERE user_id = '{user_id}';")
        time_own = cur_vote.fetchone()
        time_own = time_own[0]
        db_vote.commit()
        db_vote.close()
        return time_own


f = datetime.datetime.now().strftime("%Y%m%d")
print(type(f))
print(f)