# tools/datetime_tool.py
import requests
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from .base_tool import BaseTool
from .config import DB_PATH


class DatetimeTool(BaseTool):
    def __init__(self, gps_tool=None):
        super().__init__()
        self.gps_tool = gps_tool

    def get_local_time_by_location(self):
        if not self.gps_tool or self.gps_tool.latitude is None:
            now = datetime.now()
            return {"formatted": now.strftime("%A, %d %B %Y, %H:%M:%S"), "timezone": "Server Local"}

        tz_name = self.gps_tool.timezone 
        if not tz_name:
            # Coba fallback dari DB jika ada (opsional, tidak merusak)
            tz_name = self._get_timezone_from_db(self.gps_tool.latitude, self.gps_tool.longitude)

        if tz_name:
            try:
                local_tz = ZoneInfo(tz_name)
                now = datetime.now(local_tz)
                return {
                    "formatted": now.strftime("%A, %d %B %Y, %H:%M:%S"),
                    "timezone": tz_name,
                    "utc_offset": now.strftime('%z')
                }
            except Exception as e:
                self._log_error(f"ZoneInfo error: {e}")
        
        # Ultimate fallback
        now = datetime.now()
        return {"formatted": now.strftime("%A, %d %B %Y, %H:%M:%S"), "timezone": "Server Local"}

    def _get_timezone_from_db(self, lat: float, lon: float):
        # Fungsi ini masih dipertahankan untuk kompatibilitas, tapi lebih baik tidak digunakan
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timezone FROM location_cache
                    WHERE ABS(latitude - ?) < 0.01 AND ABS(longitude - ?) < 0.01
                    ORDER BY ABS(latitude - ?) + ABS(longitude - ?)
                    LIMIT 1
                """, (lat, lon, lat, lon))
                row = cursor.fetchone()
                if row:
                    tz = row[0]
                    self.logger.info(f"Timezone dari cache: {tz}")
                    if self.gps_tool:
                        self.gps_tool.timezone = tz
                    return tz
        except Exception as e:
            self._log_error(f"Gagal mengambil timezone dari DB: {e}")
        return None
    
    def get_current_datetime(self):
        """Mengembalikan objek datetime dengan timezone user (atau local server)"""
        if self.gps_tool and self.gps_tool.timezone:
            tz = ZoneInfo(self.gps_tool.timezone)
            return datetime.now(tz)
        # Fallback ke waktu server lokal (naive)
        return datetime.now()
    
    def get_time_phase(self):
        hour = self.get_current_datetime().hour
        
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 24:
            return "malam"
        else:
            return "dini hari"
        