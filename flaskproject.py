from flask import Flask, abort, jsonify, render_template,url_for, request,send_from_directory,redirect
import numpy as np 
import pandas as pd 
import json
import requests 
import pickle
import mysql.connector
from jikanpy import Jikan

#======================Rest API Anime=========================================
jikan = Jikan()

# ==================================Read CSV=====================================================
data=pd.read_csv('AnimeUpdatedImage.csv')
name=data[' name']

app=Flask(__name__)
# =======================================MYSQL==================================================
dbku = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='denny2310',
    auth_plugin = 'mysql_native_password',
    database='anime'
)
kursor=dbku.cursor()

userx=[]

# ===========================================Home=======================================
@app.route('/')
def home():
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
    sendx = {
        "user" : userx
    }   
    print(sendx)
    if len(userx)==0:
        return render_template('home.html',userx='Please Login')
    else:
        send=requests.post('http://127.0.0.1:5002/proses',json=sendx)
        rekomen=send.json()
        print(rekomen)
        return render_template('home.html',userx=userx[0],rekomen=rekomen["hasil"])
# ======================================Register dan Login========================================
@app.route('/register', methods=['GET','POST'])
def register():
    kursor=dbku.cursor()
    kursor.execute('describe user')
    kolom=kursor.fetchall()
    namakolom=[]
    for item in kolom:
        namakolom.append(item[0])
    kursor.execute('select * from user')
    datamysql=kursor.fetchall()
    datadict=[]
    for item in datamysql:
        x={}
        for item1 in range(len(item)):
            x[namakolom[item1]]=item[item1]
        datadict.append(x)
    listemail=[] #List Email User
    userpass={} #Dictionary username and password
    for item in datadict:
        listemail.append(item['email'])
        userpass[item['email']]=item['password']
    if len(userx)>0:
        return render_template('home.html',x='Silahkan Logout Dulu')
    else:
        if request.method=='GET':
            return render_template('register.html',x='Silahkan Sign Up')
        else:
            body=request.form
            kursor=dbku.cursor()
            if body['email']in listemail:
                return render_template('register.html',x='Email sudah terdaftar')
            else:
                qry='insert into user (email,password) values(%s,%s)'
                val=(body['email'],body['password'])
                kursor.execute(qry,val)
                dbku.commit()
                # listemail.append(body['email'])
                # userpass[body['email']]=body['password']
                return render_template('login.html',x='Selamat anda sudah terdaftar silahkan login')

@app.route('/login',methods=['POST','GET'])
def login():
    try:
        kursor=dbku.cursor()
        kursor.execute('describe user')
        kolom=kursor.fetchall()
        namakolom=[]
        for item in kolom:
            namakolom.append(item[0])
        kursor.execute('select * from user')
        datamysql=kursor.fetchall()
        datadict=[]
        for item in datamysql:
            x={}
            for item1 in range(len(item)):
                x[namakolom[item1]]=item[item1]
            datadict.append(x)
        listemail=[] #List Email User
        userpass={} #Dictionary username and password
        for item in datadict:
            listemail.append(item['email'])
            userpass[item['email']]=item['password']
        if request.method=='GET':
            if len(userx)==0:
                return render_template('login.html')
            else:
                return render_template('home.html',userx='Anda sudah login')
        else:
            body=request.form
            if body['email'] in listemail:
                if body['password']==userpass[body['email']]:
                    userx.append(body['email'])
                    return redirect('/')
                else:
                    return render_template('login.html',x='password salah')
            else:
                return render_template('login.html',x='email belum terdaftar')
    except:
        return render_template('login.html',x='Tolong input yang benar')

@app.route('/logout', methods=['GET','POST'])
def logout():
    if len(userx)==0:
        return render_template('login.html',x='Anda belum Log in')
    else:
        userx.pop()
        return render_template('home.html')
# ========================================Rekomendasi======================================
@app.route('/rekomen', methods=['GET','POST'])
def rekomen():
    if len(userx)==0:
        return render_template('login.html',x='Silakan login terlebih dahulu')
    else:
        return render_template('rekomen.html',name=name)

@app.route('/hasil', methods=['GET','POST'])
def hasil():
    body=request.values
    body=body['anime']
    send=requests.post('http://127.0.0.1:5001/proses',json=body)
    hasil=send.json()
    return render_template('hasil.html',hasil=hasil["hasil"],suka=hasil["suka"],genre=hasil["genre"],image=hasil["image"],synopsis=hasil["synopsis"])
# =============================Input Rating========================================================
@app.route('/rating', methods=['GET','POST'])
def rating():
    body=request.form
    x=body['star'].split(',')
    qry='insert into rating (user,anime,rating) values(%s,%s,%s)'
    val=(userx[0],x[1],x[0])
    kursor.execute(qry,val)
    dbku.commit()
    return render_template('home.html',x='Thank you for your rating ^_^')

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)