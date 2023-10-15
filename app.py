import pickle
import pandas as pd
from flask import Flask, render_template, request
import zipfile
import requests
from builtins import zip

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkNjYwNTAwZTE2NGQ3YWE1MjdmMzgwMzZmMzc2MzQ0OSIsInN1YiI6IjY1MmE5OTRmMzU4ZGE3MDBjNmYwZjk1YSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Bc70f35UUGqZocXyZm-jX_ErYNZ-MxUWUY5HhuLDF2s"
}

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{movie_id}?language=en-US".format(movie_id = movie_id)
    response = requests.get(url, headers=headers)
    data = response.json()
    poster_path = data["poster_path"]
    # return data['poster_path']
    return "https://image.tmdb.org/t/p/original"+ poster_path


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key = lambda x:x[1])[1:7]
    
    recommend_movies = []
    recommend_movie_posters = []
    
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        
        recommend_movies.append(movies.iloc[i[0]].title)

        # Fetch from API
        recommend_movie_posters.append(fetch_poster(movie_id))
        
    return recommend_movies, recommend_movie_posters

    


movie_dict = {}
similarity = []

with zipfile.ZipFile("pickle_files/pickle_files.zip")  as zf:
    for filename in zf.namelist():
        if filename == "movies.pkl":
            movie_dict = pickle.load(open('pickle_files/movies.pkl','rb'))
            

        if filename == "similarity.pkl":
            similarity = pickle.load(open('pickle_files/similarity.pkl', 'rb'))
            
movies = pd.DataFrame(movie_dict)

# movie_dict = pickle.load(open('pickle_files/movies.pkl','rb'))
# movies = pd.DataFrame(movie_dict)

# similarity = pickle.load(open('pickle_files/similarity.pkl', 'rb'))

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    recommended_movie = []
    movie_poster = []
    
    movie = movies['title'].values
    
    if request.method == 'POST':
        selected_movie = request.form['movie']
    else:
        selected_movie = movie[0]
        
    recommended_movie, movie_poster = recommend(selected_movie)
    
    return render_template('index.html', selected_movie = selected_movie, movies = movie, recommendations = recommended_movie, movie_poster = movie_poster, zip = zip)
    
if __name__ == '__main__':
    app.run()