import os
import random
import time
import vlc  # For audio playback

# GPIO Pin Definitions
MOTOR_1_PIN = 20  # GPIO 20, P9_41
MOTOR_2_PIN = 115  # GPIO 115, P9_27
BUTTON_PIN = 65    # GPIO 65, P8_18

# GPIO Setup
def export_gpio(pin):
    if not os.path.exists(f"/sys/class/gpio/gpio{pin}"):
        with open("/sys/class/gpio/export", "w") as f:
            f.write(str(pin))

def set_gpio_direction(pin, direction):
    with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
        f.write(direction)

def write_gpio(pin, value):
    with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
        f.write(str(value))

# Initialize GPIO Pins
def initialize_pins():
    export_gpio(MOTOR_1_PIN)
    export_gpio(MOTOR_2_PIN)
    export_gpio(BUTTON_PIN)

    set_gpio_direction(MOTOR_1_PIN, "out")
    set_gpio_direction(MOTOR_2_PIN, "out")
    set_gpio_direction(BUTTON_PIN, "in")

# Motor Control
def motor_dance():
    """Make the motors move in a dancing pattern."""
    for _ in range(10):  # Dance for 10 cycles
        write_gpio(MOTOR_1_PIN, 1)
        time.sleep(0.2)
        write_gpio(MOTOR_1_PIN, 0)
        write_gpio(MOTOR_2_PIN, 1)
        time.sleep(0.2)
        write_gpio(MOTOR_2_PIN, 0)

# Select and Play Music
def play_random_song():
    """Randomly select and play a song from ~/music."""
    music_dir = os.path.expanduser("~/music")
    songs = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]

    if not songs:
        print("No songs found in ~/music.")
        return None

    song = random.choice(songs)
    song_path = os.path.join(music_dir, song)

    instance = vlc.Instance("--aout=alsa", "--alsa-audio-device=hw:1,0")
    player = instance.media_player_new(song_path)
    player.play()

     # Wait for the player to start playing
    for _ in range(10):  # Check for up to 10 seconds
        if player.is_playing():
            return player
        time.sleep(0.5)

    print("Failed to start playback.")
    return None

# Main Function
def main():
    try:
        print("Initializing...\n")
        initialize_pins()

        print("Starting fish performance!\n")
        player = play_random_song()

        if player:
            while player.is_playing():  # While music is playing
                motor_dance()
                time.sleep(1)

        print("Performance complete.\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        print("Cleaning up GPIO...")
        write_gpio(MOTOR_1_PIN, 0)
        write_gpio(MOTOR_2_PIN, 0)
        print("GPIO cleanup complete.")

if __name__ == "__main__":
    main()
