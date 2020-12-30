
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, render_template, url_for, request, redirect, Blueprint, redirect, session
from flask_sqlalchemy import SQLAlchemy
import requests
import urllib.request
import pickle
from bs4 import BeautifulSoup
import json
import sys
import lxml
import re
from collections import OrderedDict 
import itertools
from werkzeug.security import generate_password_hash, check_password_hash
from datastore_directory import datastore

df = pd.read_csv("static/updated_movie_dataset.csv")
#df = pd.read_csv("gs://movie_dataset6/movie_dataset.csv")
features = ['keywords','cast','genres','director']
def combine_features(row):
    return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
def get_title_from_index(index):
    return df[df.index == index]["title"].values[0]
def get_index_from_title(title):
    return df[df.title == title]["index"].values[0]

def recommendation(apikey,myTitle):
    for feature in features:
        df[feature] = df[feature].fillna('')
    df["combined_features"] = df.apply(combine_features,axis=1)
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_features"])
    cosine_sim = cosine_similarity(count_matrix)

    movie_user_likes = myTitle
    movie_index = get_index_from_title(movie_user_likes)
    similar_movies =  list(enumerate(cosine_sim[movie_index]))
    sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:]
    i=0
    rec_movies=[]
    rec_posters=[]
    rec_titles=[]
    for element in sorted_similar_movies:
        #print(get_title_from_index(element[0]))
        rec_title=get_title_from_index(element[0])
        rec_titles.append(get_title_from_index(element[0]))
        #search_movie(apiKey,movie)
        response=search_movie(apikey,rec_title)
        json_str = json.dumps(response)
        resp = json.loads(json_str)
        try:
            rec_posters.append(resp['Poster'])
        except:
            rec_posters.append('static/default.png')
        i=i+1
        if i>=6:
            break
    rec_movies = {rec_titles[i]: rec_posters[i] for i in range(len(rec_titles))}
    return rec_movies

def search_movie(apiKey,movie):
    data_URL = 'http://www.omdbapi.com/?apikey='+apiKey
    year = ''
    #movie = 'Fast & Furious' 
    params = {
        't':movie,
        'type':'movie',
        'y':year,
        'plot':'full'
    }
    response = requests.get(data_URL,params=params).json()
    return response

def rec_pref(genre1 ,genre2,lang,year_range):
    temp_movies = { df["title"][i]: df["genres"][i] for i in range(len(df["title"]))}
    temp_lang = { df["title"][i]: df["original_language"][i] for i in range(len(df["title"]))}
    temp_year = { df["title"][i]: df["release_year"][i] for i in range(len(df["title"]))}
    a = year_range.split('-')
    start = int(a[0])
    end = int(a[1])
    i=0
    rec_movies=[]
    rec_title=[]
    rec_lang=[]
    rec_year=[]
    #for title1,language in temp_lang.items() :
    #    print(language)
    for title1,language in temp_lang.items() :
        if(language.find(lang) == -1):
            i
        else:
            #print(language+" "+title1)
            rec_lang.append(title1)

    for title,genres in temp_movies.items() :
        genres=str(genres)
        if (genres.find(genre1) == -1 or genres.find(genre2) == -1 ): 
            i
        else:
            rec_title.append(title)
            #print("dd"+title)

    for title,year in temp_year.items() :
        year = int(year)
        if (start <= year <= end): 
            rec_year.append(title)

    temp2=[]
    for title1 in rec_title:
        #print(title1)
        for title2 in rec_lang:
            if(title1.find(title2) == -1 ):
                i
            else:
                temp2.append(title1)
    for title1 in temp2:
        #print(title1)
        for title2 in rec_year:
            if(title1.find(title2) == -1 ):
                i
            else:
                rec_movies.append(title1)
        
              
    return rec_movies

def get_title_poster(apikey,titles):
    rec_movies=[]
    rec_posters=[]
    rec_titles=[]
    i=0
    for element in titles:
        rec_title=element
        print(rec_title)
        rec_titles.append(rec_title)
        response=search_movie(apikey,rec_title)
        json_str = json.dumps(response)
        resp = json.loads(json_str)
        try:
            rec_posters.append(resp['Poster'])
        except:
            rec_posters.append('static/default.png')
        i=i+1
        if i>=6:
            break
    rec_movies = {rec_titles[i]: rec_posters[i] for i in range(len(rec_titles))}
    return rec_movies

app = Flask(__name__)
app.secret_key = 'mysecret'

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('login.html')

@app.route('/login2',methods=['POST','GET'])
def index2():
    return render_template('login.html')

@app.route('/login',methods=['POST','GET'])
def login():
    error= ''
    if request.method == 'POST':
        print("In LOGIN/POST")
        apikey='fdbe5b4'
        #users = ['Ryan']
        genre = ['Action', 'Comedy', 'Drama', 'Horror', 'Science']
        genre_rating=[]
        user = request.form['username']
        print(user)
        login_user = datastore.get_user(user)

        print(login_user)
        
        if login_user:
            _password = request.form['pass']
            
            if check_password_hash(login_user['password'], _password):
                session['username'] = request.form['username']
                #after user logs in he is rendered to the recommendation page

                preference = datastore.get_user(user)
                Action = preference['action']
                Comedy = preference['comedy']
                Drama = preference['drama']
                Horror = preference['horror']
                Science = preference['sci-fi']
                Language = preference['language']
                Year = preference['year']

                print("Language is "+Language+"year is "+Year)

                genre_rating.append(Action)
                genre_rating.append(Comedy)
                genre_rating.append(Drama)
                genre_rating.append(Horror)
                genre_rating.append(Science)

                #appending user preferences with its username and password in DataStore
                preference = { "Action":Action, "Comedy":Comedy, "Drama":Drama, "Horror":Horror, "Science": Science}
                temp_genres=[]
                rec_movies=[]
                rec_titles=[]
                rec_genres=[]
                temp_genres = {genre[i]: genre_rating[i] for i in range(len(genre))}
                #temp_movies={key: [key, value] for key, value in zip(genre,genre_rating)}
                rec_genres=dict(reversed(sorted(temp_genres.items(), key=lambda item: item[1])))
                rec_genres= dict(itertools.islice(rec_genres.items(), 2))  
                #print(rec_genres.items())
                #genre1=rec_genres[0]
                #genre2=rec_genres[1]
                res = next(iter(rec_genres)) 
                print(res)
                genre1=res
                #genre2="Fantasy"
                rec_titles=rec_pref(genre1)
                #rec_titles.append(genre2)
                rec_movies=get_title_poster(apikey,rec_titles)
                return render_template('rec_list.html',rec_movies=rec_movies)

                # print(Action,Comedy,Horror)
                # print(Adventure,Romance,Animation)
                # return render_template('recommend.html')
        else: 
            error='User does not exist'
    return render_template('login.html',error=error)
    

@app.route('/signup',methods=['POST','GET'])
def signup():
    print("In Signup!")
    error = ''
    rexes = ('[A-Z]', '[a-z]', '[0-9]')
    
    if request.method == 'POST':
        user = request.form['username']
        existing_user = datastore.get_user(user)
        if existing_user is None:
            fullname = request.form['fullname']
            email = request.form['email']
            name = request.form['username'] 
            len_username = len(name)
            if (len_username<=15) and (name.islower()): 
                password = request.form['pass']
                len_password = len(password)
                if (len_password>=8 and len_password<=15) and (all(re.search(r, password) for r in rexes)):
                    hashpass = generate_password_hash(password)
                    datastore.save_credentials(fullname,email,name,hashpass)
                    session['username'] = request.form['username']
                    #after user registers he is taken to the preference page
                    return render_template('landingpage.html')
                else:
                    error='Password : Min 8 char & 1 digit'
                return render_template('signup.html', error=error)
            else:
                error='Username should be in lowercase'   
            return render_template('signup.html', error=error)
        else:
            error='Username already exists'
    return render_template('signup.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('login.html')
    
@app.route('/landingpage',methods=['POST','GET'])
def landingpage():
    return render_template('landingpage.html')

@app.route('/rec_list', methods=['POST','GET'])
def rec_list():
    if 'username' in session:       
        
        #we are creating a session and that session name=username
        usernamenow = session["username"]
        apikey='fdbe5b4'
        #users = ['Ryan']
        genre = ['Action', 'Comedy', 'Drama', 'Horror', 'Science']
        genre_rating=[]
        mov1 = int(request.form["mov1"])
        genre_rating.append(mov1)
        mov2 = int(request.form["mov2"])
        genre_rating.append(mov2)
        mov3 = int(request.form["mov3"])
        genre_rating.append(mov3)
        mov4 = int(request.form["mov4"])
        genre_rating.append(mov4)
        mov5 = int(request.form["mov5"])
        genre_rating.append(mov5)
        
        lang = str(request.form["lang"])
        year_range = str(request.form["myear"])

        print("language>" +lang+ "year range>" +year_range)
        datastore.save_data(usernamenow,lang,year_range)

        datastore.save_preference(usernamenow,mov1,mov2,mov3,mov4,mov5)
        temp_genres=[]
        rec_movies=[]
        rec_titles=[]
        rec_genres=[]
        temp_genres = {genre[i]: genre_rating[i] for i in range(len(genre))}
        #temp_movies={key: [key, value] for key, value in zip(genre,genre_rating)}
        rec_genres=dict(reversed(sorted(temp_genres.items(), key=lambda item: item[1])))
        rec_genres= dict(itertools.islice(rec_genres.items(), 2))  
        #print(rec_genres.items())
        #genre1=rec_genres[0]
        #genre2=rec_genres[1]
        res = next(iter(rec_genres))
        res2 = next(iter(rec_genres.popitem()))
        res1 = next(iter(rec_genres.popitem()))
        print(res1)
        print(res2)
        genre1=str(res1)
        genre2=str(res2)
        rec_titles=rec_pref(genre1,genre2,lang,year_range)
        rec_titles = list(dict.fromkeys(rec_titles))
        #rec_titles.append(genre2)
        rec_movies=get_title_poster(apikey,rec_titles)
        return render_template('rec_list.html',rec_movies=rec_movies)

@app.route('/search', methods=['POST','GET'])
def search1():
    return render_template('search.html')
def search2():
    return render_template('recommend.html')

@app.route('/recommend', methods=['POST','GET'])
def recommend():
    myTitle=request.form['myTitle']
    data = {}
    imdb_id="tt1190634"
    apikey='fdbe5b4'
    #data=url_for("http://www.omdbapi.com/?apikey=["+apikey+"]&?t="+myTitle)
    imdb_id="tt1190634"
    response=search_movie(apikey,myTitle)
    json_str = json.dumps(response)

    #load the json to a string
    resp = json.loads(json_str)

    #print the resp
    print (resp)
    try:
        imdb_id=resp['imdbID']
        poster=resp['Poster']
        year=resp['Year']
        rated=resp['Rated']
        released=resp['Released']
        runtime=resp['Runtime']
        plot=resp['Plot']
        poster=resp['Poster']
        r = requests.get(url="https://www.imdb.com/title/"+imdb_id+"/")
    except:
        return render_template('search.html')

    #extract an element in the response
    #print (resp['title'])

    # Create a BeautifulSoup object
    soup = BeautifulSoup(r.text, 'html.parser')

    #page title
    title = soup.find('title').string

    # rating
    ratingValue = soup.find("span", {"itemprop" : "ratingValue"}).string

    # no of rating given
    ratingCount = soup.find("span", {"itemprop" : "ratingCount"}).string

    # name
    titleName = soup.find("div",{'class':'titleBar'}).find("h1")
    data["name"] = titleName.contents[0].replace(u'\xa0', u'')

    
    # web scraping to get user reviews from IMDB site
    sauce = urllib.request.urlopen('https://www.imdb.com/title/'+imdb_id+'/reviews?ref_=tt_ov_rt').read()
    soup = BeautifulSoup(sauce,'lxml')
    soup_result = soup.find_all("div",{"class":"text show-more__control"})

    reviews_list = [] 
    for reviews in soup_result:
        if reviews.string:
            reviews_list.append(reviews.string) 

    #recommending movies
    rec_movies=[] 
    rec_movies=recommendation(apikey,myTitle)

    return render_template('recommend.html',year=year,released=released,runtime=runtime,plot=plot,poster=poster,myTitle=myTitle, rec_movies= rec_movies,title=title, ratingValue= ratingValue, ratingCount= ratingCount, titleName= data["name"],reviews=reviews_list)


if __name__ == "__main__":
    app.run(debug=True)
