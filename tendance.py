import sqlite3
import pandas as pd
import json


class Tendance:
    """
    Les films tendances s'affichent de manière permanente à la page d'acceuil.
    Il s'agit des n films qui ont la meilleure moyenne des scores et qui obtiennent le plus grande nombre de votes.
    """

    def __init__(self, link_data, query):
        self.query = query
        self.id_top_n_films = list()
        if 'film' in query:
            self.id_movie = 'id_film'
            self.movie = 'films'
        else:
            self.id_movie = 'id_saison'
            self.movie = 'saisons'
        self.conn = sqlite3.connect(link_data)
        self.list_film_tendance = list()

    def get_top(self, n):
        """
        :param n: nombre de films/saisons souhaité à retourner
        :return: la liste des n films/saisons qui ont la tendance.
        """
        df = pd.read_sql_query(self.query, self.conn)

        # créer une table des id et des posters
        df_poster = pd.concat([df['id_film'], df['poster']], axis=1)
        df_poster = df_poster.set_index('id_film').drop_duplicates()

        # matrice d'interaction user - item
        user_movie_df = df.pivot_table(index=['id_user'], columns=[self.id_movie], values='note')
        nb_ratings_df = self.nb_ratings_df(user_movie_df)
        moy_ratings_df = self.moy_ratings_df(user_movie_df)
        combine_df = pd.concat([nb_ratings_df, moy_ratings_df], axis=1)
        combine_df['rating_tendance'] = combine_df['nb_ratings'] * combine_df['moyenne']
        top_n_movies = combine_df.sort_values('rating_tendance', ascending=False).head(n)
        print('Top {} {} tendance:'.format(n, self.movie))
        print(top_n_movies)
        i = 1
        for id_movie in top_n_movies.index:
            poster = df_poster.loc[id_movie, 'poster']
            id_et_poster = (id_movie, poster)
            id_poster_json = dict()
            id_poster_json['id_video'] = id_movie
            self.list_film_tendance.append(id_poster_json)
            self.id_top_n_films.append(id_et_poster)
            i+=1

        with open('tendance.json', 'w') as write_file:
            json.dump(self.list_film_tendance, write_file)

        return self.list_film_tendance, self.id_top_n_films

    def nb_ratings_df(self, df):
        return df.count().to_frame(name='nb_ratings')

    def moy_ratings_df(self, df):
        return df.mean().to_frame(name='moyenne')

