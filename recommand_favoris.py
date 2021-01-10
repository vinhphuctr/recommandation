import sqlite3
import pandas as pd
import json
#----------------------------------------------#
#             METHODE ITEM_BASED               #
#----------------------------------------------#


class RecommandationFavoris:
    def __init__(self, link_data, query):
        self.query = query
        if 'film' in query:
            self._id = 'id_film'
            self.table = 'films'
        else:
            self._id = 'id_serie'
            self.table = 'series'

        self.last_id_movie_favoris = None
        self.id_users = list()
        self.conn = sqlite3.connect(link_data)
        self.cur = self.conn.cursor()
        self.list_favoris_recommand = dict()

    def get_list_recommand_favoris(self):
        self.id_users = self.get_id_user()
        for _id in self.id_users:
            top_10 = self.get_top_10(_id)
            self.list_favoris_recommand[_id] = top_10
        with open('recommand_favoris.json', 'w') as write_file:
            json.dump(self.list_favoris_recommand, write_file)
        return self.list_favoris_recommand

    def get_top_10(self, id_user):
        """
        :param n: nombre de films/séries souhaités
        :param id_user: id de l'utilisateur
        :return: la liste des n top films/séries à recommander pour l'utilisateur
        """
        df = pd.read_sql_query(self.query, self.conn)
        df['like'] = 1

        df_poster = pd.concat([df['id_film'], df['poster']], axis=1).set_index('id_film').drop_duplicates()

        matrix_users_videos = df.pivot_table(index='id_user', columns=self._id, values='like').fillna(0)

        # chercher le dernier ID vidéo ajouté
        last_id_favoris = self.get_last_id_favoris(id_user)

        # la colonne du dernier ID vidéo ajouté
        last_id_fav_col = matrix_users_videos[last_id_favoris]

        # regarder les colonnes et chercher les films/séries similaires que ce dernier
        similar_videos = matrix_users_videos.corrwith(last_id_fav_col).sort_values(ascending=False)

        # supprimer les films/séries déjà ajoutés dans le Favoris
        id_videos = matrix_users_videos.columns
        added_videos = list()
        for _id in id_videos:
            if matrix_users_videos.loc[id_user, _id] == 1:
                added_videos.append(_id)

        similar_videos_df = similar_videos.drop(added_videos).head(10).to_frame(name='similarite')

        id_top_n_movies = list()
        for _id in similar_videos_df.index:
            id_dict = dict()
            id_dict['id_video'] = _id
            id_top_n_movies.append(id_dict)

        return id_top_n_movies

    def get_id_user(self):
        id_users = list()
        list_ids = self.cur.execute('SELECT DISTINCT id_user FROM authenticate_filmfavoris').fetchall()
        for _id in list_ids:
            id_users.append(_id[0])
        return id_users

    def get_last_id_favoris(self, id_user):
        """
        :return: le dernier ID de film/série ajouté dans la BDD
        """
        query_last_favoris = '''
                             SELECT {} FROM 
                             ({} WHERE id_user = {}) 
                             ORDER BY date_ajout DESC
                             LIMIT 1'''.format(self._id, self.query, id_user)

        last_id = self.cur.execute(query_last_favoris).fetchone()[0]
        return last_id
