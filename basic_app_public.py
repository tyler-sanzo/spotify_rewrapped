from flask import Flask, render_template, request, redirect, session, url_for

import pandas as pd
import json

import spotipy
from spotipy.oauth2 import SpotifyOAuth


# import requests

login_html='''

<h1>Login Page</h1>
<br>
<form action='/login' method='post'>
	<input type='submit' value='Authenticate'>
</form>

'''

def saved_songs_cleaner(data):    
    x = []
    s = data['items']

    for i in s:
        x.append({
            'added_at': i['added_at'],
            'song': i['track']['name'],
            'album': i['track']['album']['name'],
            'artists': i['track']['artists'][0]['name'],
            'id': i['track']['id'],
            'popularity': i['track']['popularity']
        })

    return x


app = Flask(__name__)
app.secret_key = 'wowza'


auth_manager = SpotifyOAuth(
	scope='user-library-read',
	client_id='',
	client_secret='',
	redirect_uri="http://localhost:8888/",
	show_dialog=True
	)


# home route. renders index.html 
@app.route('/', methods=['GET', 'POST'])
def home():

	# template on api auth token return
	if request.args.get('code'):
		session['access_token'] = request.args.get('code')

		return render_template('logged_in.html')


	# templates on POST method
	if request.method == 'POST':

		if request.form.get('saved_tracks'):
			auth_manager.get_access_token(session.get('access_token'))
			sp = spotipy.Spotify(auth_manager=auth_manager)
			
			saved_tracks = sp.current_user_saved_tracks(limit=50, offset=0)

			df = pd.DataFrame(saved_songs_cleaner(saved_tracks))

			return render_template('user_data.html', data=df.to_html())


	# initial load in template
	return render_template('index.html')



@app.route('/login', methods=['POST'])
def login_function():

	auth_url = auth_manager.get_authorize_url()
	return redirect(auth_url)



if __name__ == '__main__':
	app.run(debug=True, port=8888)