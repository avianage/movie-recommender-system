import pickle
import pandas as pd
from flask import Flask, render_template, request
import zipfile

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key = lambda x:x[1])[1:7]
    
    recommend_movies = []
    
    for i in movie_list:
        recommend_movies.append(movies.iloc[i[0]].title)
    
    return recommend_movies     

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
    
    movie = movies['title'].values
    
    if request.method == 'POST':
        selected_movie = request.form['movie']
    else:
        selected_movie = movie[0]
        
    recommended_movie = recommend(selected_movie)
    
    return render_template('index.html', selected_movie = selected_movie, movies = movie, recommendations = recommended_movie)
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)