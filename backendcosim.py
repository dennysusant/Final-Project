from flask import Flask, abort, jsonify, render_template,url_for, request,send_from_directory,redirect
import numpy as np 
import pandas as pd 
import json
import requests 
import pickle
import mysql.connector
from jikanpy import Jikan

data=pd.read_csv('AnimeUpdatedImage.csv')
name=data[' name']
jikan = Jikan()
app=Flask(__name__)

@app.route('/proses',methods=['POST'])
def proses():
    body=request.json
    indexAnime=data[data[' name']==body].index.values[0]
    animeScore=list(enumerate(cosim[indexAnime]))
    sortAnime=sorted(animeScore,key=lambda i:i[1],reverse=True)
    idAnime=data[data[' name']==body]['animeID']
    synopsis=jikan.anime(int(idAnime))
    synopsis=synopsis['synopsis']
    anime=[]
    genre=[]
    image=[]
    for item in sortAnime[:10]:
        nama=data.iloc[item[0]][' name']
        gen=data.iloc[item[0]][' genre'].replace('[','').replace(']','').replace("'","").split(',')
        index=data.iloc[item[0]]['animeID']
        gambar=jikan.anime(int(index))
        gambar=gambar['image_url']
        image.append(gambar)
        anime.append(nama)
        genre.append(gen)
    hasilx = [[item1, item2, item3] for item1, item2, item3 in zip (anime[1:],genre[1:],image[1:])]
    return jsonify({
        "hasil":hasilx,
        "suka":anime[0],
        "genre":genre[0],
        "image":image[0],
        "synopsis":synopsis
        })


if __name__=='__main__':
    with open('cosineSimilarity.pkl','rb') as y:
        cosim=pickle.load(y)
    app.run(port=5001,debug=True)