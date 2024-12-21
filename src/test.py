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

def user_confirmation(test_name):
    while True:
        response = input(f"Ready to run the {test_name} test? (y/n/skip): ").strip().lower()
        if response in ["y", "n", "skip"]:
            return response
        print("Invalid input. Please enter 'y' to proceed, 'n' or 'skip' to skip this test.")

def initialize_pins():
    print("Initializing GPIO pins...")
    export_pins()
    set_pin_direction(pins["motor_1"], "out")
    set_pin_direction(pins["motor_2"], "out")
    set_pin_direction(pins["photoresistor"], "in")
    set_pin_direction(pins["button"], "in")
    print("Pins initialized.")

def motor_test():
    print("Testing motors (each 3 times)...")
    for i in range(3):
        print(f"Cycle {i + 1}...")
        write_pin(pins["motor_1"], 1)
        time.sleep(1)
        write_pin(pins["motor_1"], 0)
        time.sleep(1)
        write_pin(pins["motor_2"], 1)
        time.sleep(1)
        write_pin(pins["motor_2"], 0)
        time.sleep(1)
    print("Motor test complete.")

def button_test():
    print("Testing button... Press the button within 10 seconds.")
    for i in range(10):
        if read_pin(pins["button"]):
            print("Button pressed!")
            return
        time.sleep(1)
    print("Button not pressed within the timeout period.")

def photoresistor_test():
    print("Testing photoresistor...")

    # Cover test
    input("Please cover the photoresistor and press Enter to start.")
    for i in range(10):
        print(f"Light reading: {read_pin(pins["photoresistor"])}")
        if not read_pin(pins["photoresistor"]):
            print("Photoresistor detected darkness (covered).")
            break
        time.sleep(1)
    else:
        print("Photoresistor did not detect darkness within the timeout period.")

    # Light test
    input("Now shine a light on the photoresistor and press Enter to start.")
    for i in range(10):
        print(f"Light reading: {read_pin(pins["photoresistor"])}")
        if read_pin(pins["photoresistor"]):
            print("Photoresistor detected light.")
            break
        time.sleep(1)
    else:
        print("Photoresistor did not detect light within the timeout period.")

def cleanup_pins():
    print("Cleaning up GPIO...")
    for pin in pins.values():
        with open("/sys/class/gpio/unexport", "w") as f:
            f.write(str(pin))
    print("GPIO cleanup complete.")

if __name__ == "__main__":
    try:
        initialize_pins()
        
        if user_confirmation("motor") == "y":
            motor_test()
        else:
            print("Skipping motor test.")

        if user_confirmation("button") == "y":
            button_test()
        else:
            print("Skipping button test.")

        if user_confirmation("photoresistor") == "y":
            photoresistor_test()
        else:
            print("Skipping photoresistor test.")

    except KeyboardInterrupt:
        print("Test interrupted by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup_pins()
