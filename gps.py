import re
import math
import requests
import time
from functools import lru_cache
from .base_tool import BaseTool
from .exceptions import NetworkError, DataFetchError
import sqlite3
from .config import DB_PATH
from timezonefinder import TimezoneFinder

class GPSTool(BaseTool):
    def __init__(self, default_lat=None, default_lon=None, default_city=None, default_timezone=None):
        super().__init__()
        self.latitude = default_lat
        self.longitude = default_lon
        self.city = default_city
        self.country = None
        self.timezone = default_timezone
        self.tf = TimezoneFinder()
        
        if default_lat and default_lon and not default_city:
            self._reverse_geocode(default_lat, default_lon)

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371 
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    # SATU method update_location_smart dengan semua parameter opsional
    def update_location_smart(self, new_lat, new_lon, db_connection=None, user_id=None):
        """
        Update lokasi jika perpindahan > 5km.
        Parameter db_connection dan user_id opsional untuk menyimpan ke DB.
        """
        if not self.latitude or not self.longitude:
            success = self._reverse_geocode(new_lat, new_lon)
            if success and db_connection and user_id:
                self.save_to_db(user_id)
            return success

        distance_km = self._calculate_distance(self.latitude, self.longitude, new_lat, new_lon)
        if distance_km > 5.0:
            self.logger.info(f"[GPS] Perpindahan signifikan ({distance_km:.1f} km). Update lokasi...")
            success = self._reverse_geocode(new_lat, new_lon)
            if success and db_connection and user_id:
                self.save_to_db(user_id)
            return success
        else:
            self.logger.debug("[GPS] Lokasi stabil. Menggunakan data cache.")
            return False

    def _reverse_geocode(self, lat: float, lon: float) -> bool:
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {'format': 'json', 'lat': lat, 'lon': lon, 'extratags': 1, 'accept-language': 'id'}
            headers = {'User-Agent': 'AiraAI/1.0 (EfficientBot)'}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            geo_data = response.json()
            
            address = geo_data.get('address', {})
            city_keys = ['city', 'town', 'village', 'municipality', 'district']
            found_city = next((address[key] for key in city_keys if key in address), "Unknown")
            
            self.latitude = lat
            self.longitude = lon
            self.city = found_city
            self.country = address.get('country')
            
            tz_from_nominatim = geo_data.get('extratags', {}).get('timezone')
            if tz_from_nominatim:
                self.timezone = tz_from_nominatim
            else:
                self.timezone = self.tf.timezone_at(lat=lat, lng=lon) or 'Asia/Jakarta'
            
            return True
        except Exception as e:
            self.timezone = self.tf.timezone_at(lat=lat, lng=lon) or 'Asia/Jakarta'
            self.logger.error(f"Reverse geocode gagal, pakai fallback timezone: {e}")
            return False

    def get_location_context(self):
        return {
            'city': self.city, 
            'country': self.country, 
            'latitude': self.latitude, 
            'longitude': self.longitude,
            'timezone': self.timezone
        }

    @staticmethod
    @lru_cache(maxsize=128)
    def static_geocode_city(city_name: str) -> dict | None:
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {'q': city_name, 'format': 'json', 'limit': 1, 'accept-language': 'id'}
            headers = {'User-Agent': 'AiraAI/1.0 (SearchContext)'}
            resp = requests.get(url, params=params, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    first = data[0]
                    return {
                        'lat': float(first['lat']),
                        'lon': float(first['lon']),
                        'country': first.get('address', {}).get('country')
                    }
        except Exception:
            pass
        return None

    @staticmethod
    def extract_location_info(user_text: str):
        lower_text = user_text.lower()
        explicit_indicators = ['di', 'kota', 'kabupaten', 'daerah', 'wilayah', 'negara']
        has_explicit = any(ind in lower_text for ind in explicit_indicators)
        if not has_explicit:
            return {'city': None, 'explicit': False}
        
        import re
        match = re.search(r'(?:di|kota|kabupaten)\s+([A-Za-z][\w\s]+?)(?=\s+(?:dengan|hari|pada|$|,|\.))', user_text, re.IGNORECASE)
        extracted_city = match.group(1).strip().title() if match else None
        return {'city': extracted_city, 'explicit': True}

    def save_to_db(self, user_id):
        from config import AIRA_DB_PATH
        conn = sqlite3.connect(AIRA_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_settings 
            SET latitude=?, longitude=?, city=?, timezone=?
            WHERE user_id=?
        """, (self.latitude, self.longitude, self.city, self.timezone, user_id))
        conn.commit()
        conn.close()

    @classmethod
    def from_db(cls, user_id):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT latitude, longitude, city, timezone FROM user_settings WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(default_lat=row[0], default_lon=row[1], default_city=row[2], default_timezone=row[3])
        return cls()