import os
import requests
from gtts import gTTS
from datetime import datetime
import pytz
from pydub import AudioSegment

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

def read_previous_report(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

def write_current_report(file_path, report_text):
    with open(file_path, 'w') as file:
        file.write(report_text)

def delete_previous_mp3(api_key, station_id, url, folder):
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    try:
        response = requests.get(f'{url}/api/station/{station_id}/files/list?directory={folder}', headers=headers)
        if response.status_code == 200:
            files = response.json()
            if files:
                # Assume the oldest file is the one to delete
                oldest_file = sorted(files, key=lambda x: x['last_modified'])[0]['path']
                response = requests.delete(f'{url}/api/station/{station_id}/files/delete', headers=headers, json={'files': [oldest_file]})
                if response.status_code == 200:
                    return True
        return False
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
        return False

def rtx_weather_report(request):
    api_key = '6301aa8674ede3c9720a66750b4a965d'
    azura_api_key = '484aceb04796a5da:4be44d2637ccb37be7d213795d1b3f25'
    azura_station_id = '101'
    azura_url = 'https://azura.typicalmedia.net'
    weather_reports_folder = 'Weather Reports'
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
    previous_report_file = 'previous_weather_report.txt'

    log_file = open('log.txt', 'w')

    def log_message(message):
        print(message)
        log_file.write(message + '\n')

    for region, city in regions.items():
        weather_data = get_weather_data(api_key, city)
        weather_reports.append(format_weather(region, weather_data))

    tz = pytz.utc  # Set timezone to UTC
    now = datetime.now(tz)
    current_time = now.strftime("%I:%M %p")
    time_of_day = get_time_of_day(now.hour)

    intro = AudioSegment.from_mp3("rtx_weather_service_Intro.mp3")
    weather_text = f"The current time is {current_time} UTC. It's {time_of_day}. {' '.join(weather_reports)}"
    full_report_text = f"RTX Radio - Weather Report {weather_text}"

    log_message(full_report_text)

    previous_report = read_previous_report(previous_report_file)
    if previous_report == full_report_text:
        log_message("Weather report has not changed significantly. Skipping upload.")
        log_file.close()
        return 'Weather report has not changed. Skipping upload.'

    # Generate the weather report MP3 file using gTTS
    tts = gTTS(text=weather_text, lang='en')
    tts.save("weather_report.mp3")
    log_message("MP3 file created successfully!")

    # Combine the intro and weather report
    weather_report = AudioSegment.from_mp3("weather_report.mp3")
    combined_report = intro + weather_report
    combined_report.export("final_weather_report.mp3", format="mp3")
    log_message("Final MP3 file created successfully!")

    # Clean up intermediate files
    os.remove("weather_report.mp3")

    def upload_to_azuracast(api_key, station_id, url, file_path, folder):
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        files = {
            'file': open(file_path, 'rb')
        }
        log_message(f"Uploading {file_path} to AzuraCast in {folder} folder...")
        try:
            response = requests.post(
                f'{url}/api/station/{station_id}/files/upload?directory={folder}',
                headers=headers,
                files=files
            )
            if response.status_code == 200:
                log_message('File uploaded successfully to AzuraCast!')
                delete_previous_mp3(api_key, station_id, url, folder)  # Delete the oldest MP3 file
            else:
                log_message(f'Failed to upload file. Status code: {response.status_code}, Message: {response.text}')
        except Exception as e:
            log_message(f"An error occurred during the upload: {e}")

    upload_to_azuracast(azura_api_key, azura_station_id, azura_url, 'final_weather_report.mp3', weather_reports_folder)
    write_current_report(previous_report_file, full_report_text)
    log_file.close()
    return 'Weather report generated and uploaded successfully!'

if __name__ == "__main__":
    rtx_weather_report(None)
