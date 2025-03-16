import requests
from confluent_kafka import Producer
import json
import time

# Kafka configuration
conf = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(conf)

# OpenWeather API configuration
API_KEY = '560723340c54e06773ab8bf0be749132'
CITY = 'pune'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}'

# Kafka topic
TOPIC = 'openweather_data'

def fetch_weather_data():
    response = requests.get(URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_to_kafka():
    
    #while True:
        data = fetch_weather_data()
        if data:
            producer.produce(TOPIC, json.dumps(data), callback=delivery_report)
            producer.poll(0)
            producer.flush()
        time.sleep(10)  # Fetch data every 60 seconds

if __name__ == '__main__':
    produce_to_kafka()
