import os
from pathlib import Path

SECRET_KEY = os.environ.get('TOKEN_SECRET_KEY', 'test_key')

DARKSKY_API_KEY = os.environ.get("DARKSKY_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
TEST_EMAIL_ACCOUNT = os.environ.get("TEST_EMAIL_ACCOUNT")
DEFAULT_WEIGHTINGS = {'precip_probability': -10,
                      'precip_intensity': -2,
                      'cloud_cover': -5,
                      'apparent_temperature': 0}


# Since temperature is scaled roughly 10-30 in most of the world in the summer, and precipitation is scaled 0-1
# (it's a probability), it seems reasonable to make the weightings for temperature about 1/20th of the weightings
# for precipitation.
#
# For instance, a 10 degree temperature gap would be 1/20 * 10 = 0.5. Current precip probability weighting is -10,
# so the point of equality would be at p=0.05; a 5% difference in chance of rain cancels out a 10 degree temp
# difference.
#
# However I think that people probably have stronger hot-weather aversion than they do hot-weather preferences.
# So cool weather preferences are twice as impactful as hot weather preferences.
TEMPERATURE_WEIGHTINGS = {'hot': 1 / 20,
                          'neutral': 0,
                          'cool': -1 / 10}

S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID_WINE')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY_WINE')
S3_BUCKET_NAME = 'weather-window'

root = Path(__file__).parent.absolute()

GOOGLE_CREDENTIALS_PATH = root / 'credentials.json'
GOOGLE_TOKEN_PATH = root / 'token.pickle'

WEATHER_EMOJI_MAPPING = {
    'clear-day': "🌞",
    'clear-night': "🌞",
    'rain': "🌧",
    'snow': "🌨",
    'sleet': "🌨",
    'wind': "🌬",
    'fog': "🌫",
    'cloudy': "☁️",
    'partly-cloudy-day': "⛅",
    'or partly-cloudy-night': "⛅"
}
