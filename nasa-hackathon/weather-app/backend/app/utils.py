def classify_weather(temp, wind, rain, humidity):
    result = {
        "very_hot": temp > 35,
        "very_cold": temp < 5,
        "very_windy": wind > 30,
        "very_wet": rain > 20,
        "very_uncomfortable": humidity > 80
    }
    return result

