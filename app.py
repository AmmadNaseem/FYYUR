# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
from time import strftime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import *


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data=[]
    venuesRawData=Venue.query.distinct(Venue.city,Venue.state).all()
    for venue in  venuesRawData:
        filtered_venues = Venue.query.filter_by(city=venue.city,state=venue.state).all()
        print(len(filtered_venues),':dfsadfsdf',venue.city)
        num_upcoming_shows = len(list(filter(lambda x: x.start_time > datetime.today(),venue.shows)))
        venuesArray = []
        for iterate in filtered_venues:
            venuesArray.append({"id": iterate.id,"name": iterate.name,"num_upcoming_shows": num_upcoming_shows })  
        data.append({"city": venue.city,"state": venue.state,"venues": venuesArray})

    # print(data)
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term=request.form.get('search_term', '')
    venues=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    data=[]
    for item in venues:
        data.append({"id": item.id,"name": item.name,"num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(),item.shows)))})

    
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venueDetail=Venue.query.get(venue_id)
    past_shows=[]
    upcoming_shows=[]
    futureShowCount=0
    pastShowCount=0

    for futureShow in venueDetail.shows:
        if(futureShow.start_time > datetime.now()):
            futureShowCount+=1
            upcoming_shows.append({
                 "artist_id":futureShow.artists.id,
                 "artist_name": futureShow.artists.name,
                 "artist_image_link":futureShow.artists.image_link,
                 "start_time":str(futureShow.start_time)

            })

    for pastShow in venueDetail.shows:
        if(pastShow.start_time < datetime.now()):
            pastShowCount+=1
            past_shows.append({
                 "artist_id":pastShow.artists.id,
                 "artist_name": pastShow.artists.name,
                 "artist_image_link":pastShow.artists.image_link,
                 "start_time":str(pastShow.start_time)
            })

    data={
        "id": venueDetail.id,
        "name": venueDetail.name,
        "genres": json.loads(venueDetail.genres),
        "city": venueDetail.city,
        "state": venueDetail.state,
        "address": venueDetail.address,
        "phone": venueDetail.phone,
        "website": venueDetail.website,
        "facebook_link": venueDetail.facebook_link,
        "seeking_venue": venueDetail.seeking_talent,
        "seeking_description": venueDetail.seeking_description,
        "image_link":venueDetail.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": pastShowCount,
        "upcoming_shows_count": futureShowCount
     }

    # print(data)
   
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
    try:
        if request.form.get('seeking_talent') == 'y':
           seeking_talent = True
        else:
           seeking_talent = False

        venue = Venue(
            name=request.form.get('name', ''),
            city=request.form.get('city', ''),
            state=request.form.get('state', ''),
            address=request.form.get('address', ''),
            phone=request.form.get('phone', ''),
            genres=json.dumps(request.form.getlist('genres')),
            facebook_link=request.form.get('facebook_link', ''),
            website=request.form.get('website_link', ''),
            image_link=request.form.get('image_link', ''),
            seeking_talent= seeking_talent,
            seeking_description=request.form.get('seeking_description', ''),
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Venue ' + request.form['name'] + '  could not be listed.')

    finally:
        db.session.close()

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue was deleted from the list!')
    except Exception as e:
        print(e)
        db.session.rollback()
        flash('Venue could not be deleted from list.')

    finally:
        db.session.close()
    

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artistsRawData=Artist.query.all()
    data=[]
    for item in  artistsRawData:
        data.append({'id':item.id,'name':item.name})

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term=request.form.get('search_term', '')
    artists=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
    data=[]
    for item in artists:
        data.append({"id": item.id,"name": item.name,"num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.today(),item.shows)))})


    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artistDetail=Artist.query.get(artist_id)
    past_shows=[]
    upcoming_shows=[]
    futureShowCount=0
    pastShowCount=0

    for futureShow in artistDetail.shows:
        if(futureShow.start_time > datetime.now()):
            futureShowCount+=1
            upcoming_shows.append({
                 "venue_id":futureShow.venues.id,
                 "venue_name": futureShow.venues.name,
                 "venue_image_link":futureShow.venues.image_link,
                 "start_time":str(futureShow.start_time)

            })

    for pastShow in artistDetail.shows:
        if(pastShow.start_time < datetime.now()):
            pastShowCount+=1
            past_shows.append({
                 "venue_id":pastShow.venues.id,
                 "venue_name": pastShow.venues.name,
                 "venue_image_link":pastShow.venues.image_link,
                 "start_time":str(pastShow.start_time)
            })

    data={
        "id": artistDetail.id,
        "name": artistDetail.name,
        "genres": json.loads(artistDetail.genres),
        "city": artistDetail.city,
        "state": artistDetail.state,
        "phone": artistDetail.phone,
        "website": artistDetail.website,
        "facebook_link": artistDetail.facebook_link,
        "seeking_venue": artistDetail.seeking_venue,
        "seeking_description": artistDetail.seeking_description,
        "image_link":artistDetail.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": pastShowCount,
        "upcoming_shows_count": futureShowCount
     }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    item = Artist.query.get(artist_id)
    form.name.data=item.name
    form.city.data=item.city
    form.state.data=item.state
    form.phone.data=item.phone
    form.genres.data=json.loads(item.genres)
    form.image_link.data=item.image_link
    form.facebook_link.data=item.facebook_link
    form.website_link.data=item.website
    form.seeking_venue.data=item.seeking_venue
    form.seeking_description.data=item.seeking_description
    
    artist={
    'id': item.id,
    'name': item.name,
    'city': item.city,
    'state': item.state,
    'phone': item.phone,
    'genres':json.loads(item.genres),
    'image_link': item.image_link,
    'facebook_link': item.facebook_link,
    'website': item.website,
    'seeking_venue': item.seeking_venue,
    'seeking_description': item.seeking_description,
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        if request.form.get('seeking_venue') == 'y':
           seekingVenue = True
        else:
           seekingVenue = False

        artist = Artist.query.get(artist_id)
        artist.name=request.form.get('name', '')
        artist.city=request.form.get('city', '')
        artist.state=request.form.get('state', '')
        artist.phone=request.form.get('phone', '')
        artist.genres=json.dumps(request.form.getlist('genres'))
        artist.facebook_link=request.form.get('facebook_link', '')
        artist.website=request.form.get('website_link', '')
        artist.image_link=request.form.get('image_link', '')
        artist.seeking_venue= seekingVenue
        artist.seeking_description=request.form.get('seeking_description', '')

        # on successful db insert, flash success
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was updated in list!')
    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Artist ' + request.form['name'] + '  could not be updated in list.')

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    item= Venue.query.get(venue_id)
    form.name.data=item.name
    form.city.data=item.city
    form.state.data=item.state
    form.address.data=item.address
    form.phone.data=item.phone
    form.genres.data=json.loads(item.genres)
    form.image_link.data=item.image_link
    form.facebook_link.data=item.facebook_link
    form.website_link.data=item.website
    form.seeking_talent.data=item.seeking_talent
    form.seeking_description.data=item.seeking_description
    venue={
        'id': item.id,
        'name': item.name,
        'city': item.city,
        'state': item.state,
        'address': item.address,
        'phone': item.phone,
        'genres':json.loads(item.genres),
        'image_link': item.image_link,
        'facebook_link': item.facebook_link,
        'website': item.website,
        'seeking_talent': item.seeking_talent,
        'seeking_description': item.seeking_description,
        }
    
    # print(venue)
        
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        if request.form.get('seeking_talent') == 'y':
           seekingTalent = True
        else:
           seekingTalent = False

        venue = Venue.query.get(venue_id)
        venue.name=request.form.get('name', '')
        venue.city=request.form.get('city', '')
        venue.state=request.form.get('state', '')
        venue.address=request.form.get('address', '')
        venue.phone=request.form.get('phone', '')
        venue.genres=json.dumps(request.form.getlist('genres'))
        venue.facebook_link=request.form.get('facebook_link', '')
        venue.website=request.form.get('website_link', '')
        venue.image_link=request.form.get('image_link', '')
        venue.seeking_talent= seekingTalent
        venue.seeking_description=request.form.get('seeking_description', '')

        # on successful db insert, flash success
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was updated in list!')
    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Venue ' + request.form['name'] + '  could not be updated in list.')

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
    try:
        if request.form.get('seeking_venue') == 'y':
           seekingVenue = True
        else:
           seekingVenue = False

        artist = Artist(
            name=request.form.get('name', ''),
            city=request.form.get('city', ''),
            state=request.form.get('state', ''),
            phone=request.form.get('phone', ''),
            genres=json.dumps(request.form.getlist('genres')),
            facebook_link=request.form.get('facebook_link', ''),
            website=request.form.get('website_link', ''),
            image_link=request.form.get('image_link', ''),
            seeking_venue= seekingVenue,
            seeking_description=request.form.get('seeking_description', ''),
        )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Artist ' + request.form['name'] + '  could not be listed.')

    finally:
        db.session.close()

    # TODO: modify data to be the data object returned from db insertion
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows=Show.query.all()
    data=[]
    for item in  shows:
        data.append({'venue_id':item.venue_id,'venue_name':item.venues.name,'artist_id':item.artist_id,'artist_name':item.artists.name,'artist_image_link':item.artists.image_link,'start_time':item.start_time.isoformat()})
    # print(data)
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
    try:
        
        show = Show(
            venue_id=request.form.get('venue_id', ''),
            artist_id=request.form.get('artist_id', ''),
            start_time=request.form.get('start_time', ''),      
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')

    finally:
        db.session.close()

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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
# app.run(host="0.0.0.0", port=3000, debug=True)
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
