from pydantic import BaseModel

class WeatherRequest(BaseModel):
    location: str
    date: str  # YYYY-MM-DD

class WeatherResponse(BaseModel):
    very_hot: float
    very_cold: float
    very_windy: float
    very_wet: float
    very_uncomfortable: float
