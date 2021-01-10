from tendance import Tendance
from recommand_ratings import RecommandationRatings
from recommand_favoris import RecommandationFavoris
from list_users import ListUsers
from get_recomm_json import RecommJson

link_data = 'C:/Users/Epulapp/Desktop/POLYTECH 3A/Projet tutoré/wtf-api/dbV2.sqlite3'
query_films_ratings = 'SELECT rf.*, poster FROM rating_films rf JOIN films f ON rf.id_film = f.id_video'
query_saisons_ratings = 'SELECT * FROM rating_series'
query_film_favoris = 'SELECT au.*, poster FROM authenticate_filmfavoris au JOIN films f ON au.id_film = f.id_video'
query_serie_favoris = 'SELECT * FROM authenticate_seriefavoris'

# COMPOSANT 1 : Tendance pour films
tendance_films = Tendance(link_data, query_films_ratings)
list_tendance, tendance_films_top_10 = tendance_films.get_top(10)

print('\n----------------------------------------------------------------------------------------------------\n')

'''# COMPOSANT 2 : Tendance pour saisons
tendance_series = Tendance(link_data, query_saisons_ratings)
tendance_series_top_10 = tendance_series.get_top(10)
print('\nList top 10 saisons tendances :', tendance_series_top_10)

print('\n----------------------------------------------------------------------------------------------------\n')
'''
# COMPOSANT 3 : Parce que vous avez liké [dernier Film ajouté dans Favoris]
favoris_films_users = RecommandationFavoris(link_data, query_film_favoris)
favoris_films = favoris_films_users.get_list_recommand_favoris()

print('\n----------------------------------------------------------------------------------------------------\n')

'''# COMPOSANT 4 : Parce que vous avez liké [dernière Série ajoutée dans Favoris]
favoris_series_user7 = RecommandationFavoris(link_data, query_serie_favoris, 7)
favoris_series_user7_top_10 = favoris_series_user7.get_top(10)

print('\n----------------------------------------------------------------------------------------------------\n')'''

# COMPOSANT 5 : Les films recommandés pour [nomUser]
recomm_films_users = RecommandationRatings(link_data, query_films_ratings)
recomm_rating_films = recomm_films_users.get_similar_score_films()


'''
print('\n----------------------------------------------------------------------------------------------------\n')

# COMPOSANT 6 : Les saisons recommandées pour [nomUser]
recomm_saisons_user7 = RecommandationRatings(link_data, query_saisons_ratings, 7)
recomm_saisons_user7_top_10 = recomm_saisons_user7.get_top(10)
print('\nLes utilisateurs similaires ont scorés également les saisons suivantes:', recomm_saisons_user7_top_10)'''

list_id_users = ListUsers(link_data).get()

RecommJson.get_json_films(list_id_users, list_tendance, favoris_films, recomm_rating_films)

