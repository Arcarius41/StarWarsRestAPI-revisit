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
from models import db, User, Planet, Character
#from models import Person

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

@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    # serialized_characters = []
    # for character in characters:
    #     serialized_characters.append(character.serialize())
    ## ALternative way to do the same thing = the above 3 lines
    serialized_characters = list(map(lambda character: character.serialize(), characters))

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
