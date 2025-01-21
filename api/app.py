from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = "data/videotheque.json"
UPLOAD_FOLDER = "data/uploads"
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')

# Créer les dossiers si nécessaire
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(VIDEO_FOLDER, exist_ok=True)

print(f"IMAGE_FOLDER: {IMAGE_FOLDER}")
print(f"VIDEO_FOLDER: {VIDEO_FOLDER}")

def load_data():
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/films', methods=['GET'])
def get_films():
    data = load_data()
    return jsonify(data)

@app.route('/films', methods=['POST'])
def add_film():
    new_film = request.form.to_dict()
    new_film["id"] = int(new_film["id"])

    # Gérer les fichiers d'image et vidéo
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

    data = load_data()
    data.append(new_film)
    save_data(data)
    return jsonify({"message": "Film ajouté avec succès"}), 201

@app.route('/films/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    updated_film = request.form.to_dict()
    updated_film["id"] = film_id

    # Gérer les fichiers d'image et vidéo
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

    data = load_data()
    for index, film in enumerate(data):
        if film["id"] == film_id:
            data[index].update(updated_film)
            save_data(data)
            return jsonify({"message": "Film mis à jour"}), 200

    return jsonify({"error": "Film non trouvé"}), 404

@app.route('/films/<int:film_id>', methods=['DELETE'])
def delete_film(film_id):
    data = load_data()
    data = [film for film in data if film["id"] != film_id]
    save_data(data)
    return jsonify({"message": "Film supprimé"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
