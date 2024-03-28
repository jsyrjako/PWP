import requests
import datetime

def get_weather_data(start_time, end_time):
    # Convert datetime objects to ISO 8601 format
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()

    # Send GET request to BikingHub API
    response = requests.get(f'http://localhost:5000/api/weather?start_time={start_time}&end_time={end_time}')

    if response.status_code == 200:
        return response.json()
    else:
        return None

def send_to_client(weather_data):
    # Send weather data to client
    # This is a placeholder function, replace with actual implementation
    pass

def main():
    # Define time window
    start_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.now()

    # Get weather data
    weather_data = get_weather_data(start_time, end_time)

    if weather_data is not None:
        # Send weather data to client
        send_to_client(weather_data)
    else:
        print("Error retrieving weather data")

if __name__ == "__main__":
    main()