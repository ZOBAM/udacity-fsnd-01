from app import db

class Show(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  start_time = db.Column(db.DateTime, nullable = True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable = False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable = False)

  
class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = True)
    city = db.Column(db.String(120), nullable = True)
    state = db.Column(db.String(120), nullable = True)
    address = db.Column(db.String(120), nullable = True)
    phone = db.Column(db.String(120), nullable = True)
    genres = db.Column(db.String(120), nullable = True)
    image_link = db.Column(db.String(220), nullable = True)
    facebook_link = db.Column(db.String(120), nullable = True)
    website_link = db.Column(db.String(220), nullable = True)
    seeking_talent = db.Column(db.Boolean, nullable = True, default = False)
    seeking_description = db.Column(db.String(220), nullable = True)
    shows = db.relationship('Show', backref ='venues')


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable = True)
    city = db.Column(db.String(120), nullable = True)
    state = db.Column(db.String(120), nullable = True)
    phone = db.Column(db.String(120), nullable = True)
    genres = db.Column(db.String(120), nullable = True)
    image_link = db.Column(db.String(220), nullable = True)
    facebook_link = db.Column(db.String(220), nullable = True)
    website_link = db.Column(db.String(220), nullable = True)
    seeking_venue = db.Column(db.Boolean, nullable = True, default = False)
    seeking_description = db.Column(db.String(220), nullable = True)
    shows = db.relationship('Show', backref ='artists')