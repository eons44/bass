import Adafruit_BBIO.GPIO as GPIO
import time
from pydub import AudioSegment
from pydub.playback import play

# GPIO Pin Assignments
motor_1_pin = "P9_41"  # GPIO 20
motor_2_pin = "P9_27"  # GPIO 115
photoresistor_pin = "P8_9"  # GPIO 69
button_pin = "P8_18"  # GPIO 65

def initialize_pins():
    # Set up motor pins
    GPIO.setup(motor_1_pin, GPIO.OUT)
    GPIO.setup(motor_2_pin, GPIO.OUT)
    
    # Set up sensor pins
    GPIO.setup(photoresistor_pin, GPIO.IN)
    GPIO.setup(button_pin, GPIO.IN)

def motor_test():
    print("Testing motors...")
    GPIO.output(motor_1_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(motor_1_pin, GPIO.LOW)
    time.sleep(1)
    GPIO.output(motor_2_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(motor_2_pin, GPIO.LOW)
    print("Motor test complete.")

def photoresistor_test():
    print("Testing photoresistor...")
    if GPIO.input(photoresistor_pin):
        print("Light detected.")
    else:
        print("No light detected.")

def button_test():
    print("Testing button...")
    if GPIO.input(button_pin):
        print("Button pressed.")
    else:
        print("Button not pressed.")

def speaker_test():
    print("Testing speaker...")
    try:
        sound = AudioSegment.from_file("test_audio.mp3", format="mp3")
        play(sound)
        print("Speaker test complete.")
    except Exception as e:
        print(f"Speaker test failed: {e}")

def cleanup():
    print("Cleaning up GPIO...")
    GPIO.cleanup()

if __name__ == "__main__":
    try:
        print("Initializing hardware...")
        initialize_pins()
        time.sleep(1)
        
        motor_test()
        photoresistor_test()
        button_test()
        speaker_test()
        
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        cleanup()
