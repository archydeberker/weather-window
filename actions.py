import datetime
from typing import List

import pandas as pd

import cal
import models
import weather
import geo
import auth

from flask_mail import Mail

from auth import compose_verification_email

mail = Mail()


def get_forecast_for_tomorrow_from_db(location: models.Location, to_pandas=True):
    today = datetime.datetime.now()
    forecasts = models.Forecast.query.filter(models.Forecast.weather_timestamp > today,
                                            models.Forecast.location_id == location.id)

    if to_pandas:
        output = pd.read_sql(forecasts.statement, forecasts.session.bind)
    else:
        output = forecasts.all()

    return output


def add_tomorrows_forecast_to_db(location: models.Location):
    forecast = weather.DarkSky()
    hourly_forecast = forecast.get_forecast_tomorrow(location.longitude, location.latitude)

    for row in hourly_forecast.to_dict('records'):
        row['location_id'] = location.id
        forecast = models.Forecast(**row)
        models.db.session.add(forecast)

    models.db.session.commit()


def register_new_user(email: str, place: str):
    location = add_or_return_location(place)
    user = add_or_return_user(email, location)

    html = compose_verification_email(email)

    auth.send_verification_email(email, 'Please confirm your email for Weather Window', html, mail)
    print(f'Sent a verification email to {email} for {place}')
    return user


def retrieve_location_for_user(user: dict):
    user_row = models.User.query.filter_by(email=user["email"]).first()

    return models.Location.query.filter_by(id=user_row.location.id).first()


def add_or_return_location(place: str):

    location_row = get_location_by_place(place)
    if location_row is None:
        location = dict(place=place)
        location['latitude'], location['longitude'] = geo.get_lat_lon_for_place(location['place'])
        location_row = models.Location(**location)
        models.db.session.add(location_row)

    return location_row


def get_location_by_place(place: str):
    return models.Location.query.filter_by(place=place).first()


def get_user(email: str):
    return models.User.query.filter_by(email=email).first()


def add_or_return_user(email: str, location: models.Location = None):

    user_row = models.User.query.filter_by(email=email).first()
    if user_row is None:
        if location is not None:
            user_row = models.User(email=email, location=location)
            models.db.session.add(user_row)
            models.db.session.commit()
        else:
            raise ValueError('User not found and no location specified')

    return user_row


def set_email_verified(user_row: models.User):
    user_row.email_verified = True
    models.db.session.add(user_row)
    models.db.session.commit()


def update_most_recent_invite(users: List[models.User]):
    now = datetime.datetime.now()
    for u in users:
        u.most_recent_invite = now
        models.db.session.add(u)

    models.db.session.commit()


def send_tomorrow_window_to_user(user: models.User  , host: str = 'localhost'):
    calendar = cal.Calendar(host=host)
    finder = weather.WeatherWindowFinder()

    location = user.location

    # In case it's a new location
    add_tomorrows_forecast_to_db(location)

    today = datetime.date.today()
    if not needs_invite_for_tomorrow(user, today):
        print("New user already has an invite, aborting")
        return

    # Get weather forecast from DB for each of them, format as a dataframe
    forecasts_df = get_forecast_for_tomorrow_from_db(location, to_pandas=True)

    # Get the best weather for each of them
    window = finder.get_weather_window_for_forecast(forecasts_df)

    # Generate the calendar invite
    timezone = geo.get_timezone_for_lat_lon(location.latitude, location.longitude)
    event = cal.get_calendar_event(location, window, attendees=[user], timezone=timezone)

    calendar.create_event(event)
    update_most_recent_invite([user])


def filter_users_who_already_have_invites_for_today(users):
    today = datetime.date.today()
    users = [u for u in users if needs_invite_for_tomorrow(u, today)]
    return users


def needs_invite_for_tomorrow(user: models.User, today):
    if user.email == 'berkerboy@gmail.com':
        return True
    if user.most_recent_invite is None:
        return True
    if user.most_recent_invite.date() == today:
        return False
    return True