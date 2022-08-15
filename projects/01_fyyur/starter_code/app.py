#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
import os
import sys
pwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pwd)


from forms import *
from sqlalchemy import func

from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)




# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
# Controllers.
#----------------------------------------------------------------------------#




@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # group every venue per area (using the city to define the area here)
  venues_by_cities = db.session.query(Venue.city, func.count(Venue.city)).group_by(Venue.city).order_by(db.desc(Venue.city)).all()
  areas = [] 
  for city in venues_by_cities:
    areas.append(city[0])

  data = [] # this container will keep all the information needed 

  for town in areas: # query data in the database by area 
    obj = {} # this obj will define all the information per area
    st = Venue.query.filter_by(city = town).first().state
    query = Venue.query.filter_by(city=town).all()
    venues = [] # the venues variables will keep info about the venues like the id, name and upcoming show
    for venu in query:
      venue = {} # in every area , we have one or more venue, this will define info by venue
      venue['id'] = venu.id
      venue['name'] = venu.name
      venue['num_upcoming_shows'] = Venue.query.filter(Venue.name == venu.name).join(Show).filter(Show.start_time > datetime.now()).count()
      venues.append(venue)
      
    obj['city'] = town
    obj['state'] = st
    obj['venues'] = venues
    data.append(obj)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  list = []
  q = Venue.query.all() # query all the venues
  for venue in q:
    if search.lower() in venue.name.lower():
      list.append(venue)

  data = []
  for venu in list:
    obj = {}
    obj['id'] = venu.id
    obj['name'] = venu.name
    obj['num_upcoming_shows'] = Venue.query.filter(Venue.name == venu.name).join(Show).filter(Show.start_time > datetime.now()).count()
    data.append(obj)   
  
  response={
    "count": len(list),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  past_shows = [] # a containers for past shows
  upcoming_shows=[] # a container for upcoming shows

  venue  = Venue.query.get(venue_id)
  q_for_pastShows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all() # query for all past shows regarding the show start time
  q_for_upcomingShows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all() # query for all upcoming shows regarding the show start time
  for show in q_for_pastShows:
    obj = {}
    obj['artist_id'] = show.artist_id
    obj['artist_name'] = Artist.query.get(show.artist_id).name
    obj['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    obj['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    past_shows.append(obj)

  for show in q_for_upcomingShows:
    obj = {}
    obj['artist_id'] = show.artist_id
    obj['artist_name'] = Artist.query.get(show.artist_id).name
    obj['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    obj['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    upcoming_shows.append(obj)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(q_for_pastShows),
    "upcoming_shows_count": len(q_for_upcomingShows)
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion


  form = VenueForm(request.form)
  formData = request.form
  error = False 
  data = {}
  if form.validate():
    try:
    
      venue = Venue(
        name = formData['name'],
        city = formData['city'],
        state = formData['state'],
        address = formData['address'],
        phone = formData['phone'],
        genres = ','.join(formData.getlist('genres')),
        image_link = formData['image_link'],
        facebook_link = formData['facebook_link'],
        website_link = formData['website_link'],
        seeking_talent = form.seeking_talent.data,
        seeking_description = formData['seeking_description']
      )
      db.session.add(venue)
      db.session.commit()
      data['id'] = venue.id
      data['name'] = venue.name
      data['city'] = venue.city
      data['state'] = venue.state
      data['address'] = venue.address
      data['phone'] = venue.phone
      data['genres'] = venue.genres
      data['image_link'] = venue.image_link
      data['facebook_link'] = venue.facebook_link
      data['website_link'] = venue.website_link
      data['seeking_talent'] = venue.seeking_talent
      data['seeking_description'] = venue.seeking_description
      
    except:
      db.session.rollback()
      print(sys.exc_info())
      error = True
    finally:
      db.session.close()
  
  else:
    for error in form.phone.errors:
      flash(error)
    return render_template('forms/new_venue.html', form=form)

  if error:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    



  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False 
  name = ""
  venue_to_delete = Venue.query.get(int(venue_id))
  try:
    name = venue_to_delete.name
    db.session.delete(venue_to_delete)
    db.session.commit()
    print(name)
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  


  if error:
    flash('An error occurred. '+ name + ' could not be deleted.')
  else:
    flash(name  + ' was successfully deleted!')
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return name

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    artist_data = {}
    artist_data['id'] = artist.id
    artist_data['name'] = artist.name
    data.append(artist_data)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search = request.form.get('search_term', '')
  list = []
  q = Artist.query.all()
  for artist in q:
    if search.lower() in artist.name.lower():
      list.append(artist)

  data = []
  for artis in list:
    obj = {}
    obj['id'] = artis.id
    obj['name'] = artis.name
    obj['num_upcoming_shows'] = Artist.query.filter(Artist.name == artis.name).join(Show).filter(Show.start_time > datetime.now()).count()
    data.append(obj)   
  
  response={
    "count": len(list),
    "data": data
  }


  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  past_shows = []
  upcoming_shows=[]

  artist  = Artist.query.get(artist_id)
  q_for_pastShows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  q_for_upcomingShows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all()
  for show in q_for_pastShows:
    obj = {}
    obj['venue_id'] = show.venue_id
    obj['venue_name'] = Venue.query.get(show.venue_id).name
    obj['venue_image_link'] = Venue.query.get(show.venue_id).image_link
    obj['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    past_shows.append(obj)

  for show in q_for_upcomingShows:
    obj = {}
    obj['venue_id'] = show.venue_id
    obj['venue_name'] = Venue.query.get(show.venue_id).name
    obj['venue_image_link'] = Venue.query.get(show.venue_id).image_link
    obj['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    print()
    upcoming_shows.append(obj)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(q_for_pastShows),
    "upcoming_shows_count": len(q_for_upcomingShows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  current_artist = Artist.query.get(artist_id)
  
  artist={
    "id": current_artist.id,
    "name": current_artist.name,
    "genres": current_artist.genres.join(','),
    "city": current_artist.city,
    "state": current_artist.state,
    "phone": current_artist.phone,
    "website": current_artist.website_link,
    "facebook_link": current_artist.facebook_link,
    "seeking_venue": current_artist.seeking_venue,
    "seeking_description": current_artist.seeking_description,
    "image_link": current_artist.image_link
  }

   # TODO: populate form with fields from artist with ID <artist_id>

  form.name.data = current_artist.name
  form.city.data = current_artist.city
  form.state.data = current_artist.state
  form.genres.data = current_artist.genres
  form.phone.data = current_artist.phone
  form.website_link.data = current_artist.website_link
  form.facebook_link.data = current_artist.facebook_link
  form.seeking_venue.data = current_artist.seeking_venue
  form.seeking_description.data = current_artist.seeking_description
  form.image_link.data = current_artist.image_link
  
 
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes


  form = ArtistForm(request.form)
  if form.validate():
    artist = Artist.query.get(artist_id)
    try:
      formData = request.form
      artist.name = formData['name']
      artist.city = formData['city']
      artist.state = formData['state']
      artist.phone = formData['phone']
      artist.genres = ','.join(formData.getlist('genres'))
      artist.image_link = formData['image_link']
      artist.facebook_link = formData['facebook_link']
      artist.website_link = formData['website_link']
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = formData['seeking_description']

      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  N_venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.join(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.city,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link


  return render_template('forms/edit_venue.html', form=form, venue=N_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form)
  if form.validate():
    venue = db.session.query(Venue).filter_by(id = venue_id).first()
    try:
      formData = request.form
      db.session.refresh(venue)
      venue.name = formData['name']
      venue.city = formData['city']
      venue.address = formData['address']
      venue.state = formData['state']
      venue.phone = formData['phone'],
      venue.genres = ','.join(formData.getlist('genres'))
      venue.image_link = formData['image_link']
      venue.facebook_link = formData['facebook_link']
      venue.website_link = formData['website_link']
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = formData['seeking_description']
      
      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion


  form = ArtistForm(request.form)
  formData = request.form
  error = False 
  data = {}
  if form.validate():
    try:
    
      artist = Artist(
        name = formData['name'],
        city = formData['city'],
        state = formData['state'],
        phone = formData['phone'],
        genres = ','.join(formData.getlist('genres')),
        image_link = formData['image_link'],
        facebook_link = formData['facebook_link'],
        website_link = formData['website_link'],
        seeking_venue = form.seeking_venue.data,
        seeking_description = formData['seeking_description']
      )
      db.session.add(artist)
      db.session.commit()

      data['id'] = artist.id
      data['name'] = artist.name
      data['city'] = artist.city
      data['state'] = artist.state
      data['phone'] = artist.phone
      data['genres'] = artist.genres
      data['image_link'] = artist.image_link
      data['facebook_link'] = artist.facebook_link
      data['website_link'] = artist.website_link
      data['seeking_venue'] = artist.seeking_venue
      data['seeking_description'] = artist.seeking_description
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()

  else:
    for error in form.phone.errors:
      flash(error)
    return render_template('forms/new_artist.html', form=form)

  if error:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
      flash('Artist ' + formData['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []
  for show in shows:
    obj = {}
    obj['venue_id'] = show.venue_id
    obj['venue_name'] = Venue.query.get(show.venue_id).name
    obj['artist_id'] = show.artist_id
    obj['artist_name'] = Artist.query.get(show.artist_id).name
    obj['artist_image_link'] = Artist.query.get(show.artist_id).image_link
    obj['start_time'] = show.start_time.strftime("%Y-%m-%d %H:%M:%S")
    data.append(obj)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead


  form = ShowForm(request.form)
  formData = request.form
  error = False 
  
  if form.validate():
    try:
    
      show = Show(
        artist_id = formData['artist_id'],
        venue_id = formData['venue_id'],
        start_time = datetime.strptime(formData['start_time'], "%Y-%m-%d %H:%M:%S")
      
      )
      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()

    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
