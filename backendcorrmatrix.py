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

dbku = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='denny2310',
    auth_plugin = 'mysql_native_password',
    database='anime'
)


@app.route('/proses',methods=['POST'])
def proses():
    body=request.json
    kursor=dbku.cursor()
    kursor.execute('describe rating')
    kolom=kursor.fetchall()
    namakolom=[]
    for item in kolom:
        namakolom.append(item[0])
    kursor.execute('select * from rating')
    datamysql=kursor.fetchall()
    datadict=[]
    for item in datamysql:
        x={}
        for item1 in range(len(item)):
            x[namakolom[item1]]=item[item1]
            datadict.append(x)
    datadict=pd.DataFrame(datadict)
    # print(datadict)
    ratingUser=datadict[datadict['user']==body['user'][0]]
    ratings=[]
    for item,item1 in zip(ratingUser['anime'],ratingUser['rating']):
        indexanime=data[data[' name']==item]['animeID']
        rate=int(indexanime),item1
        ratings.append(rate)
    finalSkor=pd.DataFrame()
    for anime_id,rate in ratings:
        finalSkor=finalSkor.append((corrMatrix.iloc[int(anime_id)]*rate).sort_values(ascending=False))
    finalSkor=finalSkor.sum().sort_values(ascending=False)
    final=finalSkor[:8].index.values
    # print(final)
    rekomen=[]
    image=[]
    for item in final:
        x=data[data['animeID']==int(item)][' name']
        img=jikan.anime(int(item))
        img=img['image_url']
        print(list(x))
        print(img)
        if len(list(x))>0:
            rekomen.append(list(x)[0])
            image.append(img)
    hasilx = [[item1, item2] for item1, item2 in zip (rekomen,image)]
    print(hasilx)
    return jsonify({
        "hasil":hasilx
    })

if __name__=='__main__':
    with open('corrMatrix.pkl','rb') as x:
        corrMatrix=pickle.load(x)
    corrMatrix=corrMatrix.set_index('anime_id')
    app.run(port=5002,debug=True)