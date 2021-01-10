import sqlite3
import pandas as pd
import json

# ---------------------------------------------------------------------------- #
#        RECOMMANDATION DES FILMS AVEC PEARSON CORRELATION : USER_BASED        #
# ---------------------------------------------------------------------------- #

# Affichage complet de 1000 lignes et 1000 colonnes
pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)


class RecommandationRatings:
    """
    Recommandation des films/saisons pour les utilisateurs qui ont fait au moins un rating
    L'objectif est de remplir la phrase : 'Les utilisateurs (similiaires que vous) ont également scoré ces films ...'
    """
    def __init__(self, link_data, query):
        self.query = query
        self.id_users = list()
        self.id_top_n_films = list()
        self.conn = sqlite3.connect(link_data)
        self.cur = self.conn.cursor()
        if 'film' in query:
            self.id_movie = 'id_film'
            self.movie = 'films'
        else:
            self.id_movie = 'id_saison'
            self.movie = 'saisons'
        self.list_suggest_score_films = dict()

    def get_top_10(self, id_user):
        """
        :param id_user: id de l'utilisateur
        :param n: nombre de films/séries souhaités
        :return: la liste des top n films/séries
        """
        df = pd.read_sql_query(self.query, self.conn)
        note_moy = df['note'].mean()

        df_poster = pd.concat([df['id_film'], df['poster']], axis=1).set_index('id_film').drop_duplicates()

        # Convertir le dataframe précédent en forme de MATRICE : ligne = id_user, colonne = id_film/saisons, valeur = note.
        ratings = df.pivot_table(index=['id_user'], columns=[self.id_movie], values='note')

        # Eliminer les films qui ne sont pas scorés par plus de 3 users, ces films rendant la prévision moins correcte
        # Puis remplir les valeurs NaN avec des 0, sinon les NaN se considérent comme des scores négatifs.
        # S'il y avait 500 users, il serait raisonable d'enlever les films qui ne sont pas scorés par 10 users (thresh=10)
        # ==> Contrôle des thresh selon le nombre de users
        nb_users = self.cur.execute('SELECT COUNT(*) FROM user').fetchone()[0]
        thresh_user = self.control_thresh(nb_users)

        ratings = ratings.dropna(thresh=thresh_user, axis=1).fillna(0)

        self.id_top_n_films = self.recommended_films_for_user(ratings, note_moy, df_poster, id_user)
        return self.id_top_n_films

    def get_similar_score(self, titre, note, dataframe, note_moy):
        """
        Fonction de calcul des scores des films qui sont jugés 'similaires'
        :param titre: titre du film
        :param note: note de l'utilistateur pour ce film/séries
        :param dataframe: table ratings
        :param note_moy: la note moyenne de tous les films/séries
        :return: prédiction du score similaire
        """
        # Similarity matrix - standardisation les valeurs  ==> entre -1 et 1
        # CORRELATION DE PEARSON = Méthode Similarité de Cosinus centré
        # -- Soustraire les valeurs dans une ligne (à l'exception de 0) par la moyenne de leur ligne
        # -- Les valeurs résultats se stardardisent entre -1 et 1. Total des valeurs résultats dans une ligne = 0.
        # -- On a centré le rating de chaque utisateur au tour de 0 (rating initialement manquant):
        # --   + Positif rating ==> l'utilisateur aime le film plus que la moyenne
        # --   + Négatif rating ==> l'utilisateur aime le film moins que la moyenne
        item_similarity_df = dataframe.corr(method='pearson')
        similar_score = item_similarity_df[titre] * (note - note_moy)
        return similar_score

    def recommended_films_for_user(self, df, note_moy, df_poster, id_user):
        """
        :param df: la table ratings
        :param note_moy: la note moyenne de tous les films/séries
        :param id_user: id de l'utilisateur
        :return: les IDs des 10 films recommandés à cet utilisateur
        """
        # list des id des films/saisons
        ids = df.columns.tolist()

        # la liste des couples (id_movie, note), avec note > 0,
        # est la liste des films/séries déjà notés par l'utilisateur
        ids_et_notes = list()
        # scored_ids est la liste ids des films/saisons déjà scorés
        scored_ids = list()

        for _id in ids:
            note = df.loc[id_user, _id]
            # on veut la liste des films/saisons que cet utilisateur a scorés:
            # tous les films/saisons dont la note = 0 seront éliminés
            if note > 0:
                id_et_note = (_id, note)
                ids_et_notes.append(id_et_note)
                scored_ids.append(_id)

        # la liste des films/saisons similaires à ceux/celles scorés (y compris les films déjà scorés !)
        similar_films = pd.DataFrame()
        for _id, note in ids_et_notes:
            similar_films = similar_films.append(self.get_similar_score(_id, note, df, note_moy), ignore_index=True)

        # en éliminant les films déjà scorés, on obtient les films finaux à recommander à l'utilisateur
        similar_films = similar_films.drop(scored_ids, axis=1)

        # la liste des n films recommandés (dans l'ordre décroissante des scores similaires)
        top_n = similar_films.sum().sort_values(ascending=False).head(10)

        top_n_films = list()
        for _id in top_n.index:
            id_dict = dict()
            id_dict['id_film'] = _id
            top_n_films.append(id_dict)
        return top_n_films

    def get_similar_score_films(self):
        self.id_users = self.get_id_user()
        for _id in self.id_users:
            top_10 = self.get_top_10(_id)
            self.list_suggest_score_films[_id] = top_10
        with open('recommand_ratings.json', 'w') as write_file:
            json.dump(self.list_suggest_score_films, write_file)
        self.conn.close()
        return self.list_suggest_score_films

    def get_id_user(self):
        id_users = list()
        list_ids = self.cur.execute('SELECT DISTINCT id_user FROM rating_films').fetchall()
        for _id in list_ids:
            id_users.append(_id[0])
        return id_users

    def control_thresh(self, nb_users):
        if nb_users <= 10:
            thresh_user = 1
        elif 10 < nb_users <= 50:
            thresh_user = 2
        elif 50 < nb_users <= 500:
            thresh_user = 5
        elif 500 < nb_users <= 2000:
            thresh_user = 10
        elif 2000 < nb_users <= 5000:
            thresh_user = 15
        else:
            thresh_user = 20
        return thresh_user
