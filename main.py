import requests
import pyttsx3
from pydub import AudioSegment
from datetime import datetime
import pytz

def get_weather_data(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
    response = requests.get(url)
    return response.json()

def format_weather(region, weather_data):
    temp = weather_data['main']['temp']
    condition = weather_data['weather'][0]['description']
    forecast = f"In {region}, the current temperature is {temp}°F with {condition}."
    return forecast

def get_time_of_day(hour):
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 21:
        return "evening"
    else:
        return "night"

def rtx_weather_report(request):
    api_key = '6301aa8674ede3c9720a66750b4a965d'
    azura_api_key = '484aceb04796a5da:4be44d2637ccb37be7d213795d1b3f25'
    azura_station_id = '101'
    azura_url = 'https://azura.typicalmedia.net'
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

    tz = pytz.timezone('America/Detroit')
    now = datetime.now(tz)
    current_time = now.strftime("%I:%M %p")
    time_of_day = get_time_of_day(now.hour)

    intro = f"This is an RTX Weather Report! Reporting on North American weather. The current time is {current_time} {now.tzname()}. It's {time_of_day}."
    outro = "Thank you for tuning in to the RTX Weather Report. Stay safe and have a great day!"
    full_report = f"{intro} {' '.join(weather_reports)} {outro}"

    print(full_report)

    engine = pyttsx3.init()
    engine.save_to_file(full_report, 'weather_report.wav')
    engine.runAndWait()
    print("WAV file created!")  # Added this line

    try:
        sound = AudioSegment.from_wav("weather_report.wav")
        sound.export("weather_report.mp3", format="mp3")
        print("MP3 file created successfully!")  # Added this line
    except Exception as e:
        print(f"An error occurred during conversion: {e}")

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
        print(response.text)  # Added this line

    upload_to_azuracast(azura_api_key, azura_station_id, azura_url, 'weather_report.mp3')
    return 'Weather report generated and uploaded successfully!'
