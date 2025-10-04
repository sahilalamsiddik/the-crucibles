import random  # (replace with real NASA data later)

def get_weather_likelihood(location: str, date: str):
    # TODO: fetch NASA or OpenWeatherMap API
    # Example: process temperature, humidity, rainfall etc.
    
    # For demo (hackathon MVP), return dummy probabilities
    return {
        "very_hot": round(random.uniform(0, 1), 2),
        "very_cold": round(random.uniform(0, 1), 2),
        "very_windy": round(random.uniform(0, 1), 2),
        "very_wet": round(random.uniform(0, 1), 2),
        "very_uncomfortable": round(random.uniform(0, 1), 2),
    }
