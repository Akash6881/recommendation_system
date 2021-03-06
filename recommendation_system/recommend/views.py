import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
import pickle
import bs4 as bs
import requests
from nltk.stem import PorterStemmer


from .models import Search


# Create your views here.
nlp_model = pickle.load(open('./ml_data/nlp_model.pkl', 'rb'))
similarity = pickle.load(open('./ml_data/similarity.pkl', 'rb'))
tfid = pickle.load(open('./ml_data/tfid_vectorizer.pkl', 'rb'))
data = pd.read_csv('./ml_data/movie_data_with_tags.csv')

def fetch(movie_id):
    URL = 'https://api.themoviedb.org/3/movie/{}?api_key=6aeea4409e82ad77bfbe5f7beb516560&language=en-US'.format(movie_id)
    response = requests.get(URL)
    data = response.json()
    return data

def index(request):
    return render(request, 'recommend/index2.html')


def recommend(request):
    movie_name = request.GET.get('movie_name')
    search = Search(search_content = movie_name)
    search.save()
    movies_index = data[data['title'] == movie_name].index[0]



    distances = similarity[movies_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]

    recommend_movies = []
    for i in movies_list:

        movie_id = data.iloc[i[0]].id
        movie_details = fetch(movie_id)

        poster_path = 'https://image.tmdb.org/t/p/w500'+ movie_details['poster_path']

        dict = {
            'movie_name' : data.iloc[i[0]].title,
            'movie_id' : data.iloc[i[0]].id,
            'movie_poster' : poster_path,
        }
        recommend_movies.append(dict)



    stuff_for_frontend = {
        'recommends' : recommend_movies,
    }


    return render(request, 'recommend/recommend2.html', stuff_for_frontend)


def tranfromation(s):
    ps = PorterStemmer()
    s = s.lower()
    rev = s.split()
    rev = [ps.stem(word) for word in rev]
    return ' '.join(rev)

def movie_details(reqeuest, movie_id):
    movie_details = fetch(movie_id)
    imdb_id = movie_details['imdb_id']

    URL = 'https://www.imdb.com/title/{}/reviews?ref_=tt_urv'.format(imdb_id)

    response = requests.get(URL)

    soup = bs.BeautifulSoup(response.text, 'html.parser')

    soup_result = soup.find_all("div",{"class":"text show-more__control"})

    all_review = []

    for review in soup_result:
        if(review.string):

            tranformed_review = tranfromation(review.string)

            vector = tfid.transform([tranformed_review]).toarray()

            pred = nlp_model.predict(vector)

            #print(review.string)
            #print(pred)

            dict = {
                'movie_id' : movie_id,
                'review' : review.string,
                'review_pred' : pred,
            }
            all_review.append(dict)

    stuff_for_frontend = {
        'reviews' : all_review,
    }


    return render(reqeuest, 'recommend/details2.html', stuff_for_frontend)