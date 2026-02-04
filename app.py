from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from weather_service import WeatherService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = Config.CACHE_TIMEOUT

weather_service = WeatherService()

# Popular cities for quick selection
POPULAR_CITIES = [
    'London', 'New York', 'Tokyo', 'Paris', 'Sydney',
    'Dubai', 'Singapore', 'Mumbai', 'Berlin', 'Toronto',
    'Beijing', 'Moscow', 'Cairo', 'Rio de Janeiro', 'Mexico City'
]

@app.route('/')
def index():
    """Main dashboard page."""
    city = request.args.get('city', Config.DEFAULT_CITY)
    
    weather_data = weather_service.get_current_weather(city)
    if not weather_data:
        flash(f"Could not fetch weather data for '{city}'. Please try another city.", "danger")
        weather_data = weather_service.get_current_weather(Config.DEFAULT_CITY)
        if not weather_data:
            return "Error: Could not fetch weather data. Please check your API key.", 500
    
    return render_template('index.html', 
                         weather=weather_data,
                         cities=POPULAR_CITIES,
                         current_city=city)

@app.route('/forecast')
def forecast():
    """7-day forecast page."""
    city = request.args.get('city', Config.DEFAULT_CITY)
    days = min(int(request.args.get('days', 7)), 7)  # Max 7 days
    
    forecast_data = weather_service.get_forecast(city, days)
    if not forecast_data:
        flash(f"Could not fetch forecast for '{city}'. Please try another city.", "danger")
        return redirect(url_for('forecast', city=Config.DEFAULT_CITY))
    
    # Create charts
    temp_chart = weather_service.create_temperature_chart(forecast_data['forecast'])
    forecast_chart = weather_service.create_forecast_chart(forecast_data['daily_summary'])
    
    return render_template('forecast.html',
                         forecast=forecast_data,
                         temp_chart=temp_chart,
                         forecast_chart=forecast_chart,
                         cities=POPULAR_CITIES,
                         current_city=city,
                         days=days)

@app.route('/api/weather/<city>')
def api_weather(city):
    """API endpoint for weather data."""
    data = weather_service.get_current_weather(city)
    if data:
        return jsonify(data)
    return jsonify({'error': 'City not found'}), 404

@app.route('/api/forecast/<city>')
def api_forecast(city):
    """API endpoint for forecast data."""
    data = weather_service.get_forecast(city)
    if data:
        return jsonify(data)
    return jsonify({'error': 'City not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'weather-dashboard'})

@app.route('/clear_cache')
def clear_cache():
    """Clear cache (admin function)."""
    cache.clear()
    flash("Cache cleared successfully!", "success")
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('404.html', error="Internal Server Error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)