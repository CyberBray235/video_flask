from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import requests
import os

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://mongo:27017/videotheque"
mongo = PyMongo(app)
API_URL = "http://api.themoviedb.org/3"
API_KEY = '85131cf920a86abc462f9c01288d3925'
UPLOAD_FOLDER = "/api/data/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/films', methods=['GET'])
def list_films():
    response = requests.get(f'{API_URL}/movie/popular', params={'api_key': API_KEY})
    films = response.json().get('results', [])
    custom_films = list(mongo.db.films.find())
    for film in custom_films:
        film['_id'] = str(film['_id'])
    return render_template('list_films.html', films=films, custom_films=custom_films)

@app.route('/films/add', methods=['GET', 'POST'])
def add_film():
    if request.method == 'POST':
        new_film = {
            "title": request.form['title'],
            "director": request.form['director'],
            "year": request.form['year'],
            "overview": request.form['overview'],
            "poster_path": request.form['poster_path']
        }
        if 'image' in request.files:
            image = request.files['image']
            image_path = os.path.join(IMAGE_FOLDER, image.filename)
            image.save(image_path)
            new_film["image"] = os.path.join('uploads', 'images', image.filename)

        if 'video' in request.files:
            video = request.files['video']
            video_path = os.path.join(VIDEO_FOLDER, video.filename)
            video.save(video_path)
            new_film["video"] = os.path.join('uploads', 'videos', video.filename)

        result = mongo.db.films.insert_one(new_film)
        new_film['_id'] = str(result.inserted_id)  # Ajoutez cette ligne pour obtenir l'ID généré
        return redirect(url_for('list_films'))
    return render_template('add_film.html')
@app.route('/films/<int:film_id>')
def film_details(film_id):
    response = requests.get(f'{API_URL}/movie/{film_id}', params={'api_key': API_KEY})
    film = response.json()
    return render_template('film_details.html', film=film)

@app.route('/films/<film_id>/edit', methods=['GET', 'POST'])
def edit_film(film_id):
    if request.method == 'POST':
        updated_film = {
            "title": request.form['title'],
            "director": request.form['director'],
            "year": request.form['year'],
            "overview": request.form['overview'],
            "poster_path": request.form['poster_path']
        }
        mongo.db.films.update_one({'_id': ObjectId(film_id)}, {'$set': updated_film})
        return redirect(url_for('list_films'))

    film = mongo.db.films.find_one({'_id': ObjectId(film_id)})
    film['_id'] = str(film['_id'])
    return render_template('edit_film.html', film=film)
@app.route('/films/<film_id>/delete', methods=['POST'])
def delete_film(film_id):
    mongo.db.films.delete_one({'_id': ObjectId(film_id)})
    return redirect(url_for('list_films'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('data/uploads', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
