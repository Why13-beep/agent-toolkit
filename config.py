import os

DB_PATH = os.path.join('database', 'aira.db')
AIRA_DB_PATH = DB_PATH

SEARX_URLS = [ "https://searx.be/search", "https://searx.tuxcloud.net/search", 
             "https://paulgo.io/", "https://etsi.me/"]
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org"

REQUEST_TIMEOUT = 8