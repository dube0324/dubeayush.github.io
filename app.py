import pymongo
from pymongo import MongoClient
client = MongoClient("mongodb+srv://yaswanth_b:mongodb@cluster0.xwxw5yj.mongodb.net/?retryWrites=true&w=majority", connect=False)
db = client.usertable
collection = db.information
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pandas as pd
from fastapi import FastAPI, Response, status


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

#post = {"username": "testman", "password": "1234", "favourites": [888, 8864]}
#collection.insert_one(post)
#res = collection.find_one({"username": "testman"})
#print(res["password"])

def insert(username, password):
    post = {"username": username,"password":password}
    collection.insert_one(post)
    
def update(username, favourites):
    post = {"username": username, "favourites": favourites}
    collection.find_one_and_update({"username": username},{"$set": {"favourites": favourites}})  
    
def download(username):
    res = collection.find_one({"username": username})
    return res

@app.get('/')
def home():
    return "Home page"


@app.get('/registration/')
def registration(username: str, password: str):
    if(len(password)<=8):
        return {"message":"Invalid login: Password must be more than 8 characters"} 
    else:
        insert(username, password)
        return {"message" :"Succesful Registration"}

    
@app.get('/login/')
def login(username: str, password : str):
    check = collection.find_one({"username": username})
    
    if(str(type(check)) != "<class 'NoneType'>"):
        res = download(username)
        if(res["password"] != password ):
            return {"message":"Invalid login: Password does not match"}    
        
        else:
            return {"message":"Successful login"}
    else:
       return {"message":"Username doesn't exist"}           

    
@app.get('/get_favourites/')
def get_favourites(username: str):
    
    arr = download(username)
    if("favourites" not in arr.keys()):
        return {"message":"Favourites don't exist"}
    else:
        return {"result": arr["favourites"]}
    
@app.get('/update_favourites/')
def update_favourites(username: str, fav: str ):
    fav = list(map(int, fav.split(" "))) 
    update(username, fav)
    res = download(username)
    if(res["favourites"] == fav):
        return {"message": "Successfully updated"}
    else:
        return {"message":"Could not update"}
           
   
    




