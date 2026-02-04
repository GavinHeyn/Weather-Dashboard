import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from config import Config

class WeatherService:
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = Config.BASE_URL
        self.units = Config.UNITS
        self.lang = Config.LANGUAGE
    
    def get_coordinates(self, city_name):
        """Get coordinates for a city name."""
        url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': city_name,
            'limit': 1,
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon'],
                    'city': data[0]['name'],
                    'country': data[0].get('country', '')
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates: {e}")
            return None
    
    def get_current_weather(self, city_name):
        """Fetch current weather data for a city."""
        coords = self.get_coordinates(city_name)
        if not coords:
            return None
        
        url = f"{self.base_url}/weather"
        params = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'appid': self.api_key,
            'units': self.units,
            'lang': self.lang
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'city': coords['city'],
                'country': coords['country'],
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'visibility': data.get('visibility', 'N/A'),
                'clouds': data['clouds']['all'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather: {e}")
            return None
    
    def get_forecast(self, city_name, days=7):
        """Fetch 7-day weather forecast."""
        coords = self.get_coordinates(city_name)
        if not coords:
            return None
        
        url = f"{self.base_url}/forecast"
        params = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'appid': self.api_key,
            'units': self.units,
            'lang': self.lang,
            'cnt': days * 8
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            forecast_data = []
            for item in data['list']:
                forecast_data.append({
                    'datetime': datetime.fromtimestamp(item['dt']),
                    'date': datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d'),
                    'time': datetime.fromtimestamp(item['dt']).strftime('%H:%M'),
                    'temperature': round(item['main']['temp'], 1),
                    'feels_like': round(item['main']['feels_like'], 1),
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'description': item['weather'][0]['description'].title(),
                    'icon': item['weather'][0]['icon'],
                    'pop': round(item.get('pop', 0) * 100, 1)
                })
            
            return {
                'city': coords['city'],
                'country': coords['country'],
                'forecast': forecast_data,
                'daily_summary': self._create_daily_summary(forecast_data)
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def _create_daily_summary(self, forecast_data):
        """Create daily summary from 3-hour interval data."""
        if not forecast_data:
            return []
            
        df = pd.DataFrame(forecast_data)
        df['date'] = pd.to_datetime(df['date'])
        
        daily_summary = []
        for date, group in df.groupby('date'):
            daily_summary.append({
                'date': date.strftime('%Y-%m-%d'),
                'day_name': date.strftime('%A'),
                'min_temp': round(group['temperature'].min(), 1),
                'max_temp': round(group['temperature'].max(), 1),
                'avg_temp': round(group['temperature'].mean(), 1),
                'avg_humidity': round(group['humidity'].mean(), 1),
                'main_description': group['description'].mode()[0] if not group['description'].mode().empty else 'N/A',
                'icon': group['icon'].mode()[0] if not group['icon'].mode().empty else '01d',
                'pop': group['pop'].max()
            })
        
        return daily_summary
    
    def create_temperature_chart(self, forecast_data):
        """Create temperature trend chart."""
        if not forecast_data:
            return '<p>No forecast data available for chart.</p>'
            
        df = pd.DataFrame(forecast_data)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Temperature Trend', 'Humidity Trend', 
                          'Pressure Trend', 'Wind Speed'),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Temperature
        fig.add_trace(
            go.Scatter(x=df['datetime'], y=df['temperature'],
                      mode='lines+markers', name='Temperature',
                      line=dict(color='firebrick', width=2),
                      marker=dict(size=6)),
            row=1, col=1
        )
        
        # Humidity
        fig.add_trace(
            go.Scatter(x=df['datetime'], y=df['humidity'],
                      mode='lines', name='Humidity',
                      line=dict(color='royalblue', width=2),
                      fill='tozeroy'),
            row=1, col=2
        )
        
        # Pressure
        fig.add_trace(
            go.Scatter(x=df['datetime'], y=df['pressure'],
                      mode='lines', name='Pressure',
                      line=dict(color='green', width=2)),
            row=2, col=1
        )
        
        # Wind Speed
        fig.add_trace(
            go.Bar(x=df['datetime'], y=df['wind_speed'],
                  name='Wind Speed',
                  marker_color='orange'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=700,
            showlegend=False,
            template='plotly_white',
            margin=dict(t=30, b=30)
        )
        
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=1, col=2)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=2)
        
        fig.update_yaxes(title_text="°C", row=1, col=1)
        fig.update_yaxes(title_text="%", row=1, col=2)
        fig.update_yaxes(title_text="hPa", row=2, col=1)
        fig.update_yaxes(title_text="m/s", row=2, col=2)
        
        return fig.to_html(full_html=False)
    
    def create_forecast_chart(self, daily_summary):
        """Create 7-day forecast chart."""
        if not daily_summary:
            return '<p>No forecast data available for chart.</p>'
            
        df = pd.DataFrame(daily_summary)
        
        fig = go.Figure()
        
        # Add temperature range
        fig.add_trace(go.Scatter(
            x=df['day_name'], y=df['max_temp'],
            name='Max Temp',
            mode='lines+markers',
            line=dict(color='firebrick', width=2),
            marker=dict(size=10)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['day_name'], y=df['min_temp'],
            name='Min Temp',
            mode='lines+markers',
            line=dict(color='royalblue', width=2),
            marker=dict(size=10),
            fill='tonexty',
            fillcolor='rgba(65, 105, 225, 0.2)'
        ))
        
        fig.update_layout(
            title='7-Day Temperature Forecast',
            xaxis_title='Day',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            height=500
        )
        
        return fig.to_html(full_html=False)