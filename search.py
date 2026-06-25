# tools/search.py
import requests
import random
import pycountry
from .base_tool import BaseTool
from .gps import GPSTool
from .config import SEARX_URLS
from typing import Optional

class SearchTool(BaseTool):
    def __init__(self, gps_tool: GPSTool):
        super().__init__()
        self.gps = gps_tool
        self.searx_url = SEARX_URLS
        self._active_url_cache = None

    def _get_active_instance(self) -> str:
        if self._active_url_cache:
            return self._active_url_cache
        
        shuffled_urls = random.sample(self.searx_url, len(self.searx_url))

        for url in shuffled_urls:
            try:
                base_url = url.replace('/search', '')
                if requests.get(f"{base_url}/search?q=test&format=json", timeout=3).status_code == 200:
                    self._active_url_cache = url
                    self.logger.info(f"[Search] Instance aktif: {url}")
                    return url
            except requests.RequestException:
                continue

        raise Exception("Tidak ada instance SearXNG.")

    def search_news(self, query: str, city_override: Optional[str] = None):
        target_city = city_override
        country_code = None
        ctx = self.gps.get_location_context()

        if not target_city and ctx.get('city') and ctx['city'] != "Unknown":
            target_city = ctx['city']

        if target_city:
            final_query = f"{query} {target_city}"            
            if ctx.get('country'):
                try:
                    country_obj = pycountry.countries.lookup(ctx['country'])
                    if country_obj :
                        country_code = country_obj.alpha_2.lower()  # 'id' untuk Indonesia
 
                except  (LookupError, AttributeError):
                    pass
        else:
            final_query = query

        try:
            active_url = self._get_active_instance()
            params = {
                "q": final_query,
                "format": "json",
                "categories": "news",
                "language": "id"
            }
            if country_code:
                params["country"] = country_code  # filter regional
                self.logger.info(f"Searching with country filter: {country_code}")
            
            response = requests.get(active_url, params=params, timeout=8)
            response.raise_for_status()
            results = response.json().get("results", [])[:5]

            self.logger.info(f"Found {len(results)} results for '{final_query}'")
            return results
        
        except Exception as e:
            self._active_url_cache = None
            self._log_error(f"Gagal cari berita: {e}")
            return []
