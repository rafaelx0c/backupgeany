import dht11
import RPi.GPIO as GPIO
from time import sleep

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
DHT_PIN = 12
  # GPIO pin connected to the data pin of the DHT11 sensor

# Create an instance of the DHT11 sensor
sensor = dht11.DHT11(pin=DHT_PIN)

# Temperature and humidity thresholds
TEMP_THRESHOLD = 1  # Temperature threshold in Celsius
HUMIDITY_THRESHOLD = 1  # Humidity threshold in percentage

def read_dht11():
    """Read and print temperature and humidity from the DHT11 sensor, and check against thresholds."""
    result = sensor.read()
    
    if result.is_valid():
        temperature = result.temperature
        humidity = result.humidity
        
        print(f"Temperature: {temperature}C")
        print(f"Humidity: {humidity}%")
        
        if temperature > TEMP_THRESHOLD:
            print("Temperature is above threshold!")
        
        if humidity < HUMIDITY_THRESHOLD:
            print("Humidity is below threshold!")
        
    else:
        print("Failed to read from DHT11 sensor.")

if __name__ == "__main__":
    while True:
        read_dht11()
        sleep(2)  # Wait for 2 seconds before reading again
