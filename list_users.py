import sqlite3

class ListUsers():
    def __init__(self, link_data):
        self.query = 'SELECT id FROM user'
        self.cur = sqlite3.connect(link_data).cursor()

    def get(self):
        id_users =  self.cur.execute(self.query).fetchall()
        list_id_users = list()
        for _id in id_users:
            list_id_users.append(_id[0])
        list_id_users.sort()
        return list_id_users
