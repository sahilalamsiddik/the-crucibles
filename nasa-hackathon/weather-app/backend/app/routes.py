from fastapi import APIRouter
from app.models import WeatherRequest, WeatherResponse
from app.services import get_weather_likelihood

router = APIRouter()

@router.post("/weather", response_model=WeatherResponse)
def weather_endpoint(req: WeatherRequest):
    return get_weather_likelihood(req.location, req.date)
