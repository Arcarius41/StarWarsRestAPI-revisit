from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


favorite_planets = db.Table(
    "favorite_planets",
    
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("planet_id", db.ForeignKey("planet.id"), primary_key=True)
)
favorite_characters = db.Table(
    "favorite_characters",
    
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("character_id", db.ForeignKey("character.id"), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    favorite_planets = db.relationship("Planet", secondary=favorite_planets, lazy='subquery')
    favorite_characters = db.relationship("Character", secondary=favorite_characters, lazy='subquery')

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "favorite_planets": [planet.serialize() for planet in self.favorite_planets],
             "favorite_characters": [character.serialize() for character in self.favorite_characters]

            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    climate = db.Column(db.String(250))
    terrain = db.Column(db.String(250))
    population = db.Column(db.Integer)
   

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    __tablename__ = 'character'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    height = db.Column(db.Integer)
    hair_color = db.Column(db.String(250))
    eye_color = db.Column(db.String(250))
    gender = db.Column(db.String(250))
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "gender": self.gender,
            
            # do not serialize the password, its a security breach
        }


