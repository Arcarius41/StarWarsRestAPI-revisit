"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import (
    db, Planet, Character, User,
    favorite_characters, favorite_planets
)
from sqlalchemy import delete

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized_users = []
    for character in users:
        serialized_users.append(character.serialize())
    ## ALternative way to do the same thing = the above 3 lines
    # List comprehension:
    # serilized_users = [character.serialise() for character in users]
    # Map function:
    # serialized_users = list(map(lambda character: character.serialize(), users))

    response_body = {
        "msg": "Here is your list of users", "users": serialized_users
    }

    return jsonify(response_body), 200


@app.route('/users/favorites', methods=['GET'])
def get_current_favs():
    user = User.query.filter_by(username="Test user").first()
    if not user:
        db.session.merge(User(
            username="Test user",
            password="test"
        ))
        db.session.commit()
    return jsonify(
        favorite_planets=[
            planet.serialize() for planet in user.favorite_planets
        ],
        favorite_characters=[
            char.serialize() for char in user.favorite_characters
        ],
    )

# [POST] /favorite/planet/<int:planet_id> Add a new favorite planet to the current user with the planet id = planet_id.
@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_fav_planet(planet_id:int):
    # get known test user
    user = User.query.filter_by(username="Test user").first()
    if not user:
        return jsonify(msg="User doesn't exist."), 404
    # get planet by id
    planet = Planet.query.filter_by(id=planet_id).first()
    # append planet to favorite_planets on known test user
    user.favorite_planets.append(planet)
    # merge and  commit changes
    db.session.merge(user)
    db.session.commit()
    db.session.refresh(user)
    return jsonify(favorite_planets=[
        planet.serialize() for planet in user.favorite_planets
    ])


# [DELETE] /favorite/planet/<int:planet_id> Delete a favorite planet with the id = planet_id.
@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def remove_fav_planet(planet_id:int):
    user = User.query.filter_by(username="Test user").first()
    if not user:
        return jsonify(msg="User doesn't exist."), 404
    # remove planet from favorite_planets on known test user
    user.favorite_planets = list(filter(
        lambda planet: planet.id != planet_id,
        user.favorite_planets
    ))
    # merge and commit changes
    db.session.merge(user)
    db.session.commit()
    db.session.refresh(user)
    return jsonify(favorite_planets=[
        planet.serialize() for planet in user.favorite_planets
    ])


# [POST] /favorite/people/<int:people_id> Add new favorite people to the current user with the people id = people_id.
@app.route("/favorite/chars/<int:char_id>", methods=["POST"])
def add_fav_char(char_id:int):
    # get known test user
    user = User.query.filter_by(username="Test user").first()
    if not user:
        return jsonify(msg="User doesn't exist."), 404
    # get char by id
    char = Character.query.filter_by(id=char_id).first()
    # append char to favorite_characters on known test user
    user.favorite_characters.append(char)
    # commit changes
    db.session.merge(user)
    db.session.commit()


# [DELETE] /favorite/people/<int:people_id> Delete a favorite people with the id = people_id.
@app.route("/favorite/chars/<int:char_id>", methods=["DELETE"])
def remove_fav_char(char_id:int):
    # get known test user
    user = User.query.filter_by(username="Test user").first()
    # get char by id
    char = Character.query.filter_by(id=char_id).first()
    # remove char from favorite_characters on known test user
    user.favorite_characters = list(filter(
        lambda char: char.id != char_id,
        user.favorite_characters
    ))
    # commit changes
    db.session.merge(user)
    db.session.commit()
    db.session.refresh(user)
    return jsonify(favorite_characters=[char.serialize() for char in user.favorite_characters])


@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    serialized_characters = []
    for character in characters:
        serialized_characters.append(character.serialize())
    ## ALternative way to do the same thing = the above 3 lines
    # List comprehension:
    # serilized_characters = [character.serialise() for character in characters]
    # Map function:
    # serialized_characters = list(map(lambda character: character.serialize(), characters))

    response_body = {
        "msg": "Here is your list of characters", "characters": serialized_characters
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    # serialized_planets = []
    # for character in planets:
    #     serialized_planets.append(planets.serialize())
    ## ALternative way to do the same thing = the above 3 lines
    serialized_planets = list(map(lambda planets: planets.serialize(), planets))

    response_body = {
        "msg": "Here is your list of planets", "planets": serialized_planets
    }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
