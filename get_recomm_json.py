import json


class RecommJson:
    @classmethod
    def get_json_films(cls, list_id_users, films_tendance, films_favoris_suggestion, films_rating_suggestion):
        recomm_json = list()
        for id_user in list_id_users:
            user_dict = dict()
            user_dict['user'] = id_user
            user_dict['film_tendance'] = films_tendance

            found_key_favoris = False
            for key, value in films_favoris_suggestion.items():
                if key == id_user:
                    found_key_favoris = True
                    user_dict['film_favoris_suggestion'] = value
            if not found_key_favoris:
                user_dict['film_favoris_suggestion'] = None

            found_key_ratings = False
            for key, value in films_rating_suggestion.items():
                if key == id_user:
                    found_key_ratings = True
                    user_dict['film_rating_suggestion'] = value
            if not found_key_ratings:
                user_dict['film_rating_suggestion'] = None

            recomm_json.append(user_dict)

        with open('recommandations.json', 'w') as write_file:
            json.dump(recomm_json, write_file)