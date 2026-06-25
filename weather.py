# tools/weather.py
import requests
from .base_tool import BaseTool
from .gps import GPSTool

class WeatherTool(BaseTool):
    def __init__(self, gps_tool: GPSTool):
        super().__init__()
        self.gps = gps_tool
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, city_override: str = None):
        lat = lon = city_name = None

        # 1. Jika user minta kota lain → pakai static geocode (panggil Nominatim)
        if city_override:
            coords = GPSTool.static_geocode_city(city_override)
            if coords:
                lat, lon = coords['lat'], coords['lon']
                city_name = city_override
            else:
                return {"error": f"Kota '{city_override}' tidak ditemukan"}

        # 2. Jika tidak ada override → ambil dari GPS tool (RAM, tanpa API)
        else:
            if self.gps.latitude and self.gps.longitude:
                lat = self.gps.latitude
                lon = self.gps.longitude
                city_name = self.gps.city or "Lokasi Anda"
            else:
                # Fallback jika GPS tool belum punya data (misal baru mulai tanpa DB)
                return {"error": "Lokasi Anda belum diketahui. Coba nyalakan GPS atau setel lokasi manual."}

        # Panggil API cuaca Open-Meteo
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True,
                "timezone": self.gps.timezone or "auto"  # gunakan timezone dari GPS jika ada
            }
            response = requests.get(self.base_url, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()
            current = data["current_weather"]

            return {
                "temp": current["temperature"],
                "desc": self._code_to_desc(current["weathercode"]),
                "city": city_name,
                "wind_speed": current.get("windspeed"),
                "timestamp": current.get("time")
            }
        except requests.RequestException as e:
            self._log_error(f"Gagal ambil cuaca: {e}")
            return {"error": "Gagal mengambil data cuaca"}

    def _code_to_desc(self, code: int) -> str:
        """Konversi kode cuaca WMO ke deskripsi sederhana"""
        # Daftar lengkap bisa ditambah, ini contoh
        weather_codes = {
            0: "Cerah",
            1: "Cerah berawan",
            2: "Sebagian berawan",
            3: "Mendung",
            45: "Kabut",
            51: "Gerimis ringan",
            61: "Hujan ringan",
            63: "Hujan sedang",
            65: "Hujan lebat",
            71: "Salju ringan",
            80: "Hujan curah",
            95: "Badai petir"
        }
        return weather_codes.get(code, "Berawan")