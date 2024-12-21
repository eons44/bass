import os
import time

# GPIO Pin Definitions
pins = {
    "motor_1": 20,   # GPIO 20, P9_41
    "motor_2": 115,  # GPIO 115, P9_27
    "photoresistor": 69,  # GPIO 69, P8_9
    "button": 65,  # GPIO 65, P8_18
}

def export_pins():
    for name, pin in pins.items():
        if not os.path.exists(f"/sys/class/gpio/gpio{pin}"):
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(pin))

def set_pin_direction(pin, direction):
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write(direction)

def write_pin(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write(str(value))

def read_pin(pin):
    with open(f"/sys/class/gpio/gpio{pin}/value", "r") as f:
        return int(f.read().strip())

def initialize_pins():
    print("Initializing GPIO pins...")
    export_pins()
    set_pin_direction(pins["motor_1"], "out")
    set_pin_direction(pins["motor_2"], "out")
    set_pin_direction(pins["photoresistor"], "in")
    set_pin_direction(pins["button"], "in")
    print("Pins initialized.")

def motor_test():
    print("Testing motors...")
    write_pin(pins["motor_1"], 1)
    time.sleep(1)
    write_pin(pins["motor_1"], 0)
    time.sleep(1)
    write_pin(pins["motor_2"], 1)
    time.sleep(1)
    write_pin(pins["motor_2"], 0)
    print("Motor test complete.")

def photoresistor_test():
    print("Testing photoresistor...")
    value = read_pin(pins["photoresistor"])
    print(f"Photoresistor value: {'Light detected' if value else 'No light detected'}")

def button_test():
    print("Testing button...")
    value = read_pin(pins["button"])
    print(f"Button state: {'Pressed' if value else 'Not pressed'}")

def cleanup_pins():
    print("Cleaning up GPIO...")
    for pin in pins.values():
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))
    print("GPIO cleanup complete.")

if __name__ == "__main__":
    try:
        initialize_pins()
        motor_test()
        photoresistor_test()
        button_test()
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup_pins()
