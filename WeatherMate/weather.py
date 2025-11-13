import requests
import argparse
from rich.console import Console
from rich.table import Table
from config import API_KEY

console = Console()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city, units="metric"):
    """Fetch weather data from OpenWeatherMap API"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": units
    }
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        console.print(f"[red]❌ City '{city}' not found.[/red]")
    else:
        console.print(f"[red]⚠️ Error fetching data (status code: {response.status_code})[/red]")
    return None

def display_weather(data, units):
    """Display weather data in a table"""
    table = Table(title=f"Weather in {data['name']}, {data['sys']['country']} 🌍")
    table.add_column("Description", style="cyan")
    table.add_column("Temperature", style="magenta")
    table.add_column("Feels Like", style="green")
    table.add_column("Humidity", style="yellow")

    description = data["weather"][0]["description"].title()
    temp_unit = "°C" if units == "metric" else "°F"
    temperature = f"{data['main']['temp']} {temp_unit}"
    feels_like = f"{data['main']['feels_like']} {temp_unit}"
    humidity = f"{data['main']['humidity']}%"

    table.add_row(description, temperature, feels_like, humidity)
    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="🌦️ WeatherMate — Get live weather updates from the CLI")
    parser.add_argument("--city", "-c", required=True, help="City name (e.g., London, Colombo)")
    parser.add_argument("--units", "-u", choices=["metric", "imperial"], default="metric", help="Units: metric (°C) or imperial (°F)")
    args = parser.parse_args()

    data = get_weather(args.city, args.units)
    if data:
        display_weather(data, args.units)

if __name__ == "__main__":
    main()
