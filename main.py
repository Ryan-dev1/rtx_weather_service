import requests
import pyttsx3
from pydub import AudioSegment
from datetime import datetime
import pytz
import time

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

    log_file = open('log.txt', 'w')

    def log_message(message):
        print(message)
        log_file.write(message + '\n')

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

    log_message(full_report)

    engine = pyttsx3.init()
    engine.save_to_file(full_report, 'weather_report.wav')
    engine.runAndWait()
    log_message("WAV file created!")

    time.sleep(5)  # Add a delay to ensure the file is fully written

    try:
        sound = AudioSegment.from_wav("weather_report.wav")
        sound.export("weather_report.mp3", format="mp3")
        log_message("MP3 file created successfully!")
    except Exception as e:
        log_message(f"An error occurred during conversion: {e}")

    def upload_to_azuracast(api_key, station_id, url, file_path):
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        files = {
            'file': open(file_path, 'rb')
        }
        log_message(f"Uploading {file_path} to AzuraCast...")
        try:
            response = requests.post(
                f'{url}/api/station/{station_id}/files/upload',
                headers=headers,
                files=files
            )
            if response.status_code == 200:
                log_message('File uploaded successfully to AzuraCast!')
            else:
                log_message(f'Failed to upload file. Status code: {response.status_code}, Message: {response.text}')
        except Exception as e:
            log_message(f"An error occurred during the upload: {e}")

    upload_to_azuracast(azura_api_key, azura_station_id, azura_url, 'weather_report.mp3')
    log_file.close()
    return 'Weather report generated and uploaded successfully!'

if __name__ == "__main__":
    rtx_weather_report(None)
