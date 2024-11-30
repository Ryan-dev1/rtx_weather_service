import requests
import pyttsx3
from pydub import AudioSegment
from datetime import datetime
import pytz

# Function to get weather data from OpenWeatherMap
def get_weather_data(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    response = requests.get(url)
    return response.json()

# Function to format the weather data into a readable text
def format_weather(region, weather_data):
    temp = weather_data['main']['temp']
    condition = weather_data['weather'][0]['description']
    forecast = f"In {region}, the current temperature is {temp}°F with {condition}."
    return forecast

# Function to determine the time of day
def get_time_of_day(hour):
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 21:
        return "evening"
    else:
        return "night"

# Replace 'YOUR_API_KEY' with your actual API key
api_key = '6301aa8674ede3c9720a66750b4a965d'
azura_api_key = '484aceb04796a5da:4be44d2637ccb37be7d213795d1b3f25'
azura_station_id = '101'  # Your station ID from the URL
azura_url = 'https://azura.typicalmedia.net'  # Your AzuraCast URL
regions = {
    'the Northeast': 'New York',
    'the Midwest': 'Chicago',
    'the South': 'Atlanta',
    'the West': 'San Francisco',
    'the Southwest': 'Las Vegas',
    'Ontario': 'Toronto',
    'British Columbia': 'Vancouver',
    'Quebec': 'Montreal',
    'Alberta': 'Calgary'
}
weather_reports = []

for region, city in regions.items():
    weather_data = get_weather_data(api_key, city)
    weather_reports.append(format_weather(region, weather_data))

# Get the current time and timezone
tz = pytz.timezone('America/Detroit')
now = datetime.now(tz)
current_time = now.strftime("%I:%M %p")
time_of_day = get_time_of_day(now.hour)

# Create the full report with an intro and outro
intro = f"This is an RTX Weather Report! Reporting on North American weather. The current time is {current_time} {now.tzname()}. It's {time_of_day}."
outro = "Thank you for tuning in to the RTX Weather Report. Stay safe and have a great day!"
full_report = f"{intro} {' '.join(weather_reports)} {outro}"

# Print the weather report
print(full_report)

# Generate the .wav file using pyttsx3
engine = pyttsx3.init()
engine.save_to_file(full_report, 'weather_report.wav')
engine.runAndWait()

# Convert the .wav file to .mp3 using pydub
try:
    sound = AudioSegment.from_wav("weather_report.wav")
    sound.export("weather_report.mp3", format="mp3")
    print("MP3 file created successfully!")
except Exception as e:
    print(f"An error occurred during conversion: {e}")

# Upload the MP3 file to AzuraCast using the API
def upload_to_azuracast(api_key, station_id, url, file_path):
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    files = {
        'file': open(file_path, 'rb')
    }
    response = requests.post(
        f'{url}/api/station/{station_id}/files/upload',
        headers=headers,
        files=files
    )
    if response.status_code == 200:
        print('File uploaded successfully to AzuraCast!')
    else:
        print(f'Failed to upload file. Status code: {response.status_code}, Message: {response.text}')

# Upload the generated MP3 file to AzuraCast
upload_to_azuracast(azura_api_key, azura_station_id, azura_url, 'weather_report.mp3')


