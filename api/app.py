from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory,flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
from datetime import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server')))

from models import User


app = Flask(__name__)
app.secret_key = 'Tchad'

app.config["MONGO_URI"] = "mongodb://mongo:27017/videotheque"
mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


API_URL = "http://api.themoviedb.org/3"
API_KEY = '85131cf920a86abc462f9c01288d3925'



@app.route('/api/films', methods=['GET'])
def get_films():
    films = list(mongo.db.films.find())
    for film in films:
        film['_id'] = str(film['_id'])
    return jsonify(films)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    existing_user = User.check_by_username(username, mongo)
    if existing_user:
        return jsonify({"message": "Nom d'utilisateur déjà pris. Veuillez en choisir un autre."}), 409
    role = 'admin' if username == 'admin' else 'user'
    user = User(None, username, None, role)
    user.set_password(password)
    mongo.db.users.insert_one({'username': username, 'password': user.password, 'role': role})
    return jsonify({"message": "Inscription Réussie. Veuillez vous connecter"}), 201


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id,mongo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.check_by_username(username,mongo)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('list_films'))
        flash('Nom d\'utilisateur ou mot de passe invalide')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



#Nous voudrions que l'admin valide les pret des films avant de les rendre disponible
#Nous allons donc ajouter une fonctionnalité pour que l'admin puisse voir les films loués
#et les valider
@app.route('/admin/validate_rental/<rental_id>', methods=['POST'])
@login_required
def validation_pret(rental_id):
    if current_user.role != 'admin':
        flash('Oups mon grand tu n\'est pas admin')
        return redirect(url_for('index'))
    rental = mongo.db.rentals.find_one({"_id": ObjectId(rental_id)})
    if rental:
        mongo.db.rentals.update_one({"_id": ObjectId(rental_id)}, {"$set": {"validated": True}})
        flash('Un admin à validé le pret')
    else:
        flash('Location Introuvable')
    return redirect(url_for('admin'))

# pour valider l'ajout d'un film
@app.route('/admin/validate_film/<film_id>', methods=['POST'])
@login_required
def validation_ajout_film(film_id):
    if current_user.role != 'admin':
        flash('Reviens quand tu seras admin')
        return redirect(url_for('index'))
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    if film:
        mongo.db.films.update_one({"_id": ObjectId(film_id)}, {"$set": {"validated": True}})
        flash('Un admin à validé le film')
    else:
        flash('Film introuvable')
    return redirect(url_for('admin'))

@app.route('/admin/dashboard')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Soyez admin pour accéder à cette page')
        return redirect(url_for('index'))
    users = list(mongo.db.users.find())
    rentals = list(mongo.db.rentals.find({"validated": {"$ne": True}}))
    films = list(mongo.db.films.find({"validated": {"$ne": True}}))
    return render_template('admin.html',users=users, rentals=rentals, films=films)


"""
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.check_by_username(username, mongo)
        if existing_user:
            flash('Nom d\'utilisateur déjà pris. Veuillez en choisir un autre.')
            return redirect(url_for('register'))
        role = 'admin' if username == 'admin' else 'user'
        user = User(None, username, None, role)
        user.set_password(password)
        mongo.db.users.insert_one({'username': username, 'password': user.password, 'role': role})
        flash('Inscription Réussie. Veuillez vous connecter')
        return redirect(url_for('login'))
    return render_template('register.html')
"""


#On veut que l'admin puisse sup ou modifier un user

@app.route('/admin/delete_user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        #On verifie si l'user est admin
        flash('Accès non autorisé')
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        flash('Utilisateur supprimé avec succès')
    else:
        flash('Utilisateur introuvable')
    return redirect(url_for('admin'))

@app.route('/admin/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Accès non autorisé')
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash('Utilisateur introuvable')
        return redirect(url_for('admin')) #On redirige vers la page admin

    if request.method == 'POST':
        username = request.form['username']
        role = request.form['role']
        mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": username, "role": role}})
        flash('Utilisateur modifié avec succès')
        return redirect(url_for('admin'))

    return render_template('edit_user.html', user=user)



@app.route('/search', methods=['GET', 'POST'])
@login_required
def recherche():
    query = request.args.get('query')
    if query:
        response = requests.get(f'{API_URL}/search/movie', params={'api_key': API_KEY, 'query': query})
        films = response.json().get('results', [])
        for film in films:
            if not mongo.db.films.find_one({"tmdb_id": film['id']}):
                mongo.db.films.insert_one({
                    "tmdb_id": film['id'],
                    "title": film['title'],
                    "overview": film['overview'],
                    "poster_path": f"https://image.tmdb.org/t/p/w500{film['poster_path']}" if film['poster_path'] else None,
                    "release_date": film.get('release_date', 'Date inconnue!')
                })
#Là on recupère aussi les fims disponibles sur mongo
        custom_films = list(mongo.db.films.find({"tmdb_id": {"$in": [film['id'] for film in films]}}))
        for film in custom_films:
            film['_id'] = str(film['_id'])
            film['id'] = film['_id'] #Pour notre template car si on le met pas le template ne connaitra pas le id
        return render_template('list_films.html', films=custom_films, sort_by=None)
    return render_template('recherche.html')

@app.route('/films/rent/<film_id>', methods=['POST'])
@login_required
def loca_film(film_id):
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    if film:
        rental ={
            "user_id": current_user.id,
            "film_id": film_id,
            "validated": False
        }
        mongo.db.rentals.insert_one(rental)
        flash('Votre demande de location est en attente de validation par un admin.')
    else:
        flash('Film non trouvé')
    return redirect(url_for('list_films'))

@app.route('/films/return/<film_id>', methods=['POST'])
@login_required
def resti_film(film_id):
    resti = mongo.db.rentals.find_one({"user_id": current_user.id, "film_id": film_id})
    if resti:
        mongo.db.rentals.delete_one({"_id": resti['_id']})
        flash('Vous avez retourné avec succès')
    else:
        flash('Location introuvable')
    return redirect(url_for('list_films'))

@app.route('/profile')
@login_required
def profile():
    rentals = list(mongo.db.rentals.find({"user_id": current_user.id, "validated": True}))
    loca_en_attente = list(mongo.db.rentals.find({"user_id": current_user.id, "validated": False}))
    films_loues = []
    for rental in rentals:
        film = mongo.db.films.find_one({"_id": ObjectId(rental['film_id'])})
        if film:
            film['_id'] = str(film['_id'])
            films_loues.append(film)
    films_en_attente = []
    for rental in loca_en_attente:
        film = mongo.db.films.find_one({"_id": ObjectId(rental['film_id'])})
        if film:
            film['_id'] = str(film['_id'])
            films_en_attente.append(film)
    return render_template('profile.html', user=current_user, rentals=films_loues, loca_en_attente=films_en_attente)

@app.route('/films/add', methods=['GET', 'POST'])
@login_required
def add_film():
    if request.method == 'POST':
        new_film = {
            "title": request.form['title'],
            "director": request.form['director'],
            "year": request.form['year'],
            "overview": request.form['overview'],
            "poster_path": request.form['poster_path']
        }

        result = mongo.db.films.insert_one(new_film)
        new_film['_id'] = str(result.inserted_id)  # Ajoutez cette ligne pour obtenir l'ID généré
        return redirect(url_for('list_films'))
    return render_template('add_film.html')
"""
@app.route('/films/<film_id>', methods=['GET'])
@login_required
def film_details(film_id):
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    if film:
        response = requests.get(f'{API_URL}/movie/{film["tmdb_id"]}', params={'api_key': API_KEY})
        films = response.json()
        return render_template('film_details.html', film=films)
    else:
        flash('Pas de details pour ce film')
        return redirect(url_for('list_films'))
"""

@app.route('/api/films/<film_id>', methods=['GET'])
def api_film_details(film_id):
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    if film:
        response = requests.get(f'{API_URL}/movie/{film["tmdb_id"]}', params={'api_key': API_KEY})
        film_details = response.json()
        return jsonify(film_details), 200
    else:
        return jsonify({"message": "Film non trouvé"}), 404

@app.route('/films/<film_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_film(film_id):
    if request.method == 'POST':
        updated_film = {
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
            updated_film["image"] = os.path.join('uploads', 'images', image.filename)

        if 'video' in request.files:
            video = request.files['video']
            video_path = os.path.join(VIDEO_FOLDER, video.filename)
            video.save(video_path)
            updated_film["video"] = os.path.join('uploads', 'videos', video.filename)

        mongo.db.films.update_one({'_id': ObjectId(film_id)}, {'$set': updated_film})
        return redirect(url_for('list_films'))

    film = mongo.db.films.find_one({'_id': ObjectId(film_id)})
    film['_id'] = str(film['_id'])
    return render_template('edit_film.html', film=film)

@app.route('/films/<film_id>/delete', methods=['POST'])
@login_required
def delete_film(film_id):
    mongo.db.films.delete_one({'_id': ObjectId(film_id)})
    return redirect(url_for('list_films'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('data/uploads', filename)

@app.route('/health')
def health_check():
    try:
        return {'status': 'healthy', 'service': 'api'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
