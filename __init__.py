# tools/__init__.py
from .base_tool import BaseTool
from .exceptions import ToolError, NetworkError, DataFetchError
from .gps import GPSTool
from .datetime_tool import DatetimeTool
from .weather import WeatherTool
from .search import SearchTool
from .manager import ToolManager
from .prompt import get_tools_instruction
from .config import DB_PATH, AIRA_DB_PATH, SEARX_URLS, WEATHER_URL, REQUEST_TIMEOUT

# Menggabungkan semua tools ke dalam satu class utama untuk diakses
class Tools:
    def __init__(self, default_lat=None, default_lon=None, default_city=None):
        "Inisiasi dan koneksi antar tools"
        self.gps = GPSTool(default_lat=default_lat, default_lon=default_lon, default_city=default_city)
        self.datetime = DatetimeTool(gps_tool= self.gps)
        self.weather = WeatherTool(gps_tool=self.gps)
        self.search = SearchTool(gps_tool=self.gps)

    def get_all_tools(self):
        # Mengambalikan dict semua tools.
        return {
            'gps': self.gps,
            'datetime': self.datetime,
            'weather': self.weather,
            'search': self.search,
        }
    
# Pastikan nama class Tools bisa diakses dari luar
__all__ = ['Tools', 'ToolManager', 'get_tools_instruction',
           'BaseTool', 'ToolError', 'NetworkError', 'DataFetchError',
           'GPSTool', 'DatetimeTool', 'WeatherTool', 'SearchTool',
           'DB_PATH', 'AIRA_DB_PATH', 'SEARX_URL', 'WEATHER_URL', 'REQUEST_TIMEOUT']