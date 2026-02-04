import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 600))
    
    # Default values
    DEFAULT_CITY = os.getenv('DEFAULT_CITY', 'London')
    UNITS = 'metric'  # metric, imperial, standard
    LANGUAGE = 'en'