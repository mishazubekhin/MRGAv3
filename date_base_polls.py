import datetime
import sqlite3


# Добавление столбцов
# db_vote = sqlite3.connect("tguser.db")
# cur_vote = db_vote.cursor()
# cur_vote.execute("""ALTER TABLE polls ADD COLUMN check_time TEXT""")
# db_vote.commit()


class User_polls(object):
    db_vote = sqlite3.connect("tguser.db")
    cur_vote = db_vote.cursor()
    cur_vote.execute("""CREATE TABLE IF NOT EXISTS user_polls (
        rowid,
        user_id INT,
        poll_id INTEGER,
        photos BLOB);
        """)
    db_vote.commit()
    db_vote.close()


    def add_poll(self, user_id, poll_id, photo):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"INSERT INTO user_polls (user_id, poll_id, photos) VALUES ('{user_id}', '{poll_id}', '{photo}');")
        db_vote.commit()
        db_vote.close()


    def return_poll(self, user_id):
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT poll_id FROM user_polls WHERE user_id = '{user_id}';")
        user_polls_all = cur_vote.fetchall()
        user_poll_all_list = []
        for i in reversed(user_polls_all):
            user_poll_all_list.append(i[0])
            if len(user_poll_all_list) <= 2:
                continue
            else:
                break
        db_vote.commit()
        cur_vote.execute(f"SELECT photos FROM user_polls WHERE user_id = '{user_id}';")
        user_photo_all = cur_vote.fetchall()
        user_photo_all_list = []
        for i in reversed(user_photo_all):
            user_photo_all_list.append(i[0])
            if len(user_photo_all_list) <= 2:
                continue
            else:
                break
        db_vote.commit()
        db_vote.close()
        return [user_poll_all_list, user_photo_all_list]


    def return_user_id(self, user_id: int) -> bool:
        db_vote = sqlite3.connect("tguser.db")
        cur_vote = db_vote.cursor()
        cur_vote.execute(f"SELECT user_id FROM user_polls WHERE user_id = '{user_id}'")
        user_id_any = cur_vote.fetchone()
        db_vote.close()
        print(user_id_any)
        return user_id_any == None



