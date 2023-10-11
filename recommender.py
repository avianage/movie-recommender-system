import pandas as pd
import ast      # For converting a String of Lists to a List
from sklearn.feature_extraction.text import CountVectorizer     # For vectorization
from nltk.stem.porter import PorterStemmer  # For Stemming Words
from sklearn.metrics.pairwise import cosine_similarity
import pickle

movies = pd.read_csv('dataset/tmdb_5000_movies.csv')
credit = pd.read_csv('dataset/tmdb_5000_credits.csv')

movies = movies.merge(credit, on='title')

# We need to make sure that which tags we keep.
# Genre, ID, Keywords, Original language, Title, Overview, Cast, Crew

movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast','crew']]

movies.dropna(inplace=True)

# Following Data should be converted to a list:
# [{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 14, "name": "Fantasy"}, 
# {"id": 878, "name": "Science Fiction"}]

# ['Action','Adventure','Fantasy','SciFi']

# Pre-processing:

def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
        
    return L

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

def convertCast(obj):
    L = []
    count = 0
    for i in ast.literal_eval(obj):
        if count!= 3:        
            L.append(i['name'])
            count += 1
        else:
            break
    return L

movies['cast'] = movies['cast'].apply(convertCast)

def getDirector(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
        
    return L

movies['crew'] = movies['crew'].apply(getDirector)

movies['overview'] = movies['overview'].apply(lambda x:x.split())

# Problem Faced in the list: We need to remove the space between the List Elements

movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ", "") for i in x])

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Remove un-necessary columns

new_df = movies[['movie_id','title','tags']]

new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())

# Word Stemming: ('love', 'loving','loved') will become ('love','love','love')
ps = PorterStemmer()

# Helper Function
def stem(text):
    y = []
    
    for i in text.split():
        y.append(ps.stem(i))
        
    return " ".join(y)

# Stemming should be applied to the newest data frame
new_df['tags'] = new_df['tags'].apply(stem)



# We need to convert these tags into vectors as the Recommender can give inaccurate result

cv = CountVectorizer(max_features=5000, stop_words="english")

vectors = cv.fit_transform(new_df['tags']).toarray()

# Now we need to find the distance between all vectors.
# As we are working with higher dimentional array of vectors, we shouldnt use Euclidian Distance
# as it can be inaccurate. Hence, we find Cosine Distance i.e angles.

similarity = cosine_similarity(vectors)

# We dont find distance but similarity as similarity is always between 0 and 1 and it is 
# easier to calculate than the distance

def recommend(movie):
    movie_index = new_df[new_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key = lambda x:x[1])[1:6]
    
    for i in movie_list:
        print(new_df.iloc[i[0]].title)
        
        
pickle.dump(new_df.to_dict(), open('movies.pkl','wb'))
pickle.dump(similarity, open('similarity.pkl','wb'))