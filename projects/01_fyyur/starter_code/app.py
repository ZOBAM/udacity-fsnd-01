#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ast import arguments
from email.policy import default
import json
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helper functions
#----------------------------------------------------------------------------#
def get_shows(owner_id, owner = 'artist', type = 'future', join_on = False):
  # a function to fetch shows based on provided arguments
  owner_attr = owner+'_id'

  if join_on:
    join_class = Venue
  else:
    join_class = Artist

  if type == 'past':
    shows = db.session.query(Show).join(join_class).filter(getattr(Show,owner_attr) == owner_id).filter(Show.start_time<datetime.now()).all()
  else:
    shows = db.session.query(Show).join(join_class).filter(getattr(Show,owner_attr) == owner_id).filter(Show.start_time>datetime.now()).all()
  if owner == 'venue':
    data = []
    for show in shows:
      data.append({
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link":show.artists.image_link,
        "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
      })
    shows = data
  
  return [shows, len(shows)]
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  venues = Venue.query.all()
  data=[]
  
  places = set()
  print('the length of venue is: ', len(venues))
  num_of_places = len(venues)
  i = 0
  while i < num_of_places:
    places.add((venues[i].city,venues[i].state))
    i += 1

  for venue in places:
    current_venues = Venue.query.filter_by(state = venue[1], city = venue[0]).all()
    venues = []
    for current_venue in current_venues:
      venues.append({
        'id': current_venue.id,
        'name': current_venue.name,
        'num_upcoming_show': get_shows(owner_id=current_venue.id, owner='venue',join_on=True)[1]
      })
    data.append({
      "city":venue[0],
      "state":venue[1],
      "venues":venues
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term')
  query_results = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  data = []
  for result in query_results:
    data.append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': get_shows(owner = 'venue', owner_id = result.id)[1]
    })
    
  response = {
    'count': query_results.count(),
    'data': data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  venue = Venue.query.filter_by(id=venue_id).first()

  upcoming_shows = get_shows(owner_id= venue_id, owner='venue')
  past_shows = get_shows(owner_id= venue_id, owner='venue', type='past')

  data = {
    "id":venue.id,
    "name": venue.name,
    "genres": venue.genres.strip('{}').split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows[0],
    "upcoming_shows": upcoming_shows[0],
    "past_shows_count": past_shows[1],
    "upcoming_shows_count":upcoming_shows[1]
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()

  # TODO: insert form data as a new Venue record in the db, instead
  try:
    venue = Venue(
      name=form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone=form.phone.data,
      image_link=form.image_link.data,
      facebook_link = form.facebook_link.data,
      genres=form.genres.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      website_link = form.website_link.data
      )
    db.session.add(venue)
    db.session.commit()
    data = venue
    flash('Venue ' + data.name + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    shows = Show.query.filter_by(venue_id = venue_id).all()
    for show in shows:
      db.session.delete(show)
    venue = Venue.query.filter_by(id = venue_id).first()
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return json.dumps({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')
  query_results = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  data = []
  for result in query_results:
    data.append({
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': get_shows(result.id)[1]
    })
  response = {
    'count': query_results.count(),
    'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first()

  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows_data = []

  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows_data = []

  for show in past_shows:
    past_shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link":show.venues.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  for show in upcoming_shows:
    upcoming_shows_data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "venue_image_link":show.venues.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })

  data = {
    "id":artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('{}').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows_data,
    "upcoming_shows":upcoming_shows_data,
    "past_shows_count": len(past_shows_data),
    "upcoming_shows_count":len(upcoming_shows_data)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id = artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = ArtistForm()
    Artist.query.filter_by(id = artist_id).update(dict(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    ))
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id = venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = VenueForm()
    Venue.query.filter_by(id = venue_id).update(dict(
      name=form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link = form.facebook_link.data,
        genres=form.genres.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data,
        website_link = form.website_link.data
    ))
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm()
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()

    flash('Artist ' + artist.name + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()
    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []

  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id":show.artist_id,
      "artist_name":Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id =show.artist_id).first().image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()
  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = form.start_time.data
    show = Show(artist_id = artist_id, venue_id = venue_id, start_time = start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
