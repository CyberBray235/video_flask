from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import requests
import os

app = Flask(__name__)

API_URL = "http://api:5000/films"
UPLOAD_FOLDER = "/app/data/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/films')
def list_films():
    response = requests.get(API_URL)
    films = response.json()
    return render_template('list_films.html', films=films)

@app.route('/films/add', methods=['GET', 'POST'])
def add_film():
    if request.method == 'POST':
        data = {
            "id": request.form['id'],
            "title": request.form['title'],
            "director": request.form['director'],
            "year": request.form['year']
        }
        files = {
            'image': request.files['image'],
            'video': request.files['video']
        }
        requests.post(API_URL, data=data, files=files)
        return redirect(url_for('list_films'))
    return render_template('add_film.html')

@app.route('/films/<int:film_id>/edit', methods=['GET', 'POST'])
def edit_film(film_id):
    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "director": request.form['director'],
            "year": request.form['year']
        }
        files = {}
        if 'image' in request.files:
            files['image'] = request.files['image']
        if 'video' in request.files:
            files['video'] = request.files['video']
        requests.put(f"{API_URL}/{film_id}", data=data, files=files)
        return redirect(url_for('list_films'))

    response = requests.get(API_URL)
    films = response.json()
    film = next((f for f in films if f['id'] == film_id), None)
    return render_template('edit_film.html', film=film)

@app.route('/films/<int:film_id>/delete', methods=['POST'])
def delete_film(film_id):
    requests.delete(f"{API_URL}/{film_id}")
    return redirect(url_for('list_films'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
