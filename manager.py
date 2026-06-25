# tools/ manager.py

from typing import Dict, List, Optional
import json
from . import Tools

class ToolManager:
    # Mengelola semua tools dan integrasi dengan LLM func calling

    def __init__ (self, tools: Tools):
        self.tools = tools
    
    def get_definitions(self) -> List[Dict]:
        # Definisi tools untuk calling
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather information for a city. Use when user asks about weather, temperature, rain, or hot/cold conditions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name (e.g., Jakarta, Surabaya, Medan). Extract from user's question."    
                            }
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for current news, information, or facts. Use when user asks about recent events, news, or things you don't know.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., berita terbaru, apa itu AI, kabar terkini)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_datetime",
                    "description": "Get current date and time in user's location.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_location",
                    "description": "Get user's current location information.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
        ]
    
    def execute(self, tool_name: str, arguments: Dict) -> str:
        try:
            if tool_name == "get weather":
                return self._execute_weather(arguments)
            elif tool_name == "search_web":
                return self. _execute_search(arguments)
            elif tool_name == "get_datetime":
                return self._execute_datetime()
            elif tool_name == "get_location":
                return self._execute_location()
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
        
    def _execute_weather(self, arguments: Dict) -> str:
        city = arguments.get("city", "")
        weather_data = self.tools.weather.get_weather(city_override=city)
        if weather_data and "error" not in weather_data:
            return f"Weather in {weather_data['city']}: {weather_data['temp']}°C,{weather_data['desc']}"
        return f"Could not get weather for '{city}'. City may not be found."
    
    def _execute_search(self, arguments: Dict) -> str:
        query = arguments.get("query", "")
        results = self.tools.search.search_news(query)
        if results:
            snippets = []
            for r in results[:3]:
                title = r.get('title', '')
                content = r.get('content', '')[:150]
                snippets.append(f"-{title}: {content}")
            return "Search results:\n" + "\n". join(snippets)
        return f"No search results found for '{query}'."
    
    def _execute_datetime(self) -> str:
        dt = self.tools.datetime.get_local_time_by_location()
        return f"Current time: {dt['formatted']} ({dt.get('timezone', 'Local')})"
    
    def _execute_location(self) -> str:
        ctx = self.tools.gps.get_location_context()
        if ctx.get('city') and ctx ['city'] != "Unknown":
            return f"Location: {ctx['city']}, {ctx.get('country', 'Unknown')}"
        return "Location not set or unknown."