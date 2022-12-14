import numpy as np
import pandas as pd
 
import pandas as pd
import numpy as np
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware
from collections import OrderedDict 

data = pd.read_csv('combined_data.csv')
movies = pd.read_csv('movies-clean.csv', index_col = 'movieId')
links = pd.read_csv('links.csv', index_col = 'movieId')

    
pivot_table = data.pivot(index = 'movieId', columns = 'userId', values = 'rating').fillna(0)
content_based_info = pd.DataFrame(data.drop(columns = ['title', 'userId', 'timestamp', '(no genres listed)']).groupby(by = 'movieId').mean())
ids = np.array(links[['tmdbId']]).ravel()


app = FastAPI(debug = True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


def show_recommendations(movieId):    
    movieId = get_mid(movieId)  
    
    def collaborative_cosine(movieId, data):    
        movie_indices = data.index   
        index = np.where(movie_indices == movieId)    
        movie_similarity_cosine = cosine_similarity(data)
        similarities = movie_similarity_cosine[index].ravel()    
        closest = np.argpartition(similarities, -11)[-11:]
        recommended_movie_indices = movie_indices[closest].tolist()    
        if movieId in recommended_movie_indices:
            recommended_movie_indices.remove(movieId)    
        recommended_movies = movies.loc[np.array(recommended_movie_indices),:].index.tolist()
        return recommended_movies
    
    
    result = []
    for i in range(0,len(movieId)):
            result.extend(collaborative_cosine(movieId[i], pivot_table))        
    result = list(dict.fromkeys(result))
    result = content_based_info.loc[result,:].sort_values(by = 'rating').index[0:10]
    result = movies.loc[result,'disptitle']
    mid = get_id(result)      
    return get_tid(mid)

def get_tid(arr):
    arr = [int(i) for i in arr]     
    tid = links.loc[arr, 'tmdbId']
    tid = [int(i) for i in tid]    
    return tid

def get_mid(arr):
    arr = [int(i) for i in arr] 
    mid = []
    for i in arr:        
        mid.append(links.index[links['tmdbId']==i].values[0])
    
    return mid

def display_movies(arr): #displays names of movies given movieIds
    res = []
    for id in arr:       
        
        res.append(movies.loc[movies.index==id, 'disptitle'].iloc[0])
    return res

def title_search(query):
    query_list = query.split(' ')
    cleaned_list = [ x for x in query_list if x != '' ]
    results = set(movies['disptitle'])
    for i in cleaned_list:
        res_list = movies.loc[movies['disptitle'].str.contains(i, case=False) == True, 'disptitle']
        for j in res_list:
            results = results.intersection(res_list)
    return list(results)

def query_results(query):
    results_dict = {}
    values = title_search(query)
    keys = []
    for i in list(values):
        keys.append(str(movies.loc[movies.disptitle==i].index.values[0]))
    keys = get_tid(keys)
    results_dict = dict(zip(keys,values))
    final_results = OrderedDict(results_dict.items())
    
    return { "result":list(final_results.keys())}

def cold_start():
    highly_rated = content_based_info.sort_values(by=['rating'], ascending = False).index.values[0:20]    
    return { "result" : get_tid(highly_rated) }

def get_id(names):
    id = []
    for name in names:
        id.append(movies[movies['disptitle'] == name].index.tolist()[0])
    
    
    return id


@app.get('/')
def home():
    return "Home page"

@app.get('/recommendations/')
def recommendations(options: str):
    
    options = list(map(int, options.split(" "))) 
    result = show_recommendations(options)
    
    if(len(result)==0):
        return {"result":"no recommendations"}   
    elif(set(options).issubset(set(ids))):
        return {"result":result} 
    else:       
        return {"result":"not in tmdbid"}
   
   
    

@app.get('/search/{query}')
def search(query:str):    
    return query_results(query)

@app.get('/cold_start/')
def cold():
    return cold_start()
