import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
import pickle


# Create your views here.

similarity = pickle.load(open('./ml_data/similarity.pkl', 'rb'))

data = pd.read_csv('./ml_data/movie_data_with_tags.csv')

def index(request):
    return render(request, 'recommend/index.html')


def recommend(request):
    movie_name = request.GET.get('movie_name')

    movies_index = data[data['title'] == movie_name].index[0]

    distances = similarity[movies_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]
    s = []
    for i in movies_list:
        s.append(data.iloc[i[0]].title)


    stuff_for_frontend = {
        'recommends' : s
    }


    return render(request, 'recommend/recommend.html', stuff_for_frontend)