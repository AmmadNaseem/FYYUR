from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment


# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Models.
# ----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__='Show'
    id=db.Column(db.Integer, primary_key=True)
    artist_id=db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id=db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}> Venue={self.venues} Artist={self.artists}"

    


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref=('venues'))

    def __repr__(self):
         return f"<Venue id={self.id} name={self.name} city={self.city} state={self.state} address={self.address} phone={self.phone} genres={self.genres} facebook_link={self.facebook_link} image_link={self.image_link} website={self.website} seeking_talent={self.seeking_talent} seeking_description={self.seeking_description}>"


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref=('artists'))

    def __repr__(self):
        return f"<Artist id={self.id} name={self.name} city={self.city} state={self.state} phone={self.phone} genres={self.genres} facebook_link={self.facebook_link} image_link={self.image_link} website={self.website} seeking_venue={self.seeking_venue} seeking_description={self.seeking_description}>"
