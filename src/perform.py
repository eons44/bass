import os
import random
import time
import json
import subprocess
import eons

class GPIOUtils:
    @staticmethod
    def export_gpio(pin):
        if not os.path.exists(f"/sys/class/gpio/gpio{pin}"):
            with open("/sys/class/gpio/export", "w") as f:
                f.write(str(pin))

    @staticmethod
    def unexport_gpio(pin):
        if os.path.exists(f"/sys/class/gpio/gpio{pin}"):
            with open("/sys/class/gpio/unexport", "w") as f:
                f.write(str(pin))

    @staticmethod
    def set_gpio_direction(pin, direction):
        with open(f"/sys/class/gpio/gpio{pin}/direction", "w") as f:
            f.write(direction)

    @staticmethod
    def write_gpio(pin, value):
        with open(f"/sys/class/gpio/gpio{pin}/value", "w") as f:
            f.write(str(value))

    @staticmethod
    def read_gpio(pin):
        with open(f"/sys/class/gpio/gpio{pin}/value", "r") as f:
            return int(f.read().strip())

class Fish:
    def __init__(this):
        this.audio = eons.util.DotDict()
        this.audio.manifest = None
        this.audio.volume = 0.05  # VLC gain value (e.g., 5% volume)

        with open(os.path.expanduser("~/music.json")) as f:
            this.audio.manifest = json.load(f)

        this.pin = eons.util.DotDict()
        this.pin.output = eons.util.DotDict()
        this.pin.output.motor = eons.util.DotDict()
        this.pin.output.motor.tail = 20  # GPIO 20, P9_41 (Tail)
        this.pin.output.motor.mouth = 115  # GPIO 115, P9_27 (Mouth)
        this.input = eons.util.DotDict()
        this.input.button = 65  # GPIO 65, P8_18

        GPIOUtils.export_gpio(this.pin.output.motor.tail)
        GPIOUtils.export_gpio(this.pin.output.motor.mouth)
        GPIOUtils.export_gpio(this.input.button)

        GPIOUtils.set_gpio_direction(this.pin.output.motor.tail, "out")
        GPIOUtils.set_gpio_direction(this.pin.output.motor.mouth, "out")
        GPIOUtils.set_gpio_direction(this.input.button, "in")

        this.current = eons.util.DotDict()
        this.current.song = None
        this.current.tempo = None
        this.current.process = None

        print("Initialization complete.")

    def destroy(this):
        GPIOUtils.write_gpio(this.pin.output.motor.tail, 0)
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 0)

        GPIOUtils.unexport_gpio(this.pin.output.motor.tail)
        GPIOUtils.unexport_gpio(this.pin.output.motor.mouth)
        GPIOUtils.unexport_gpio(this.input.button)

        if this.current.process:
            this.current.process.terminate()

        print("Cleanup complete.")

    def worker(this):
        """Main worker function."""
        print("Starting worker...")
        while True:
            if GPIOUtils.read_gpio(this.input.button):
                print("Button pressed!")
                this.play_random_song()
                this.motor_dance_to_beat(this.detect_tempo())
            time.sleep(0.5)

    def detect_tempo(this):
        """Detect the tempo (BPM) of the song."""
        print(f"Tempo for {this.current.song} is {this.current.tempo} ms / beat.")
        return this.current.tempo

    def toggle_mouth(this):
        """Toggle the mouth motor."""
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 1)
        time.sleep(0.2)
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 0)

    def toggle_tail(this):
        """Toggle the tail motor."""
        GPIOUtils.write_gpio(this.pin.output.motor.tail, 1)
        time.sleep(0.4)
        GPIOUtils.write_gpio(this.pin.output.motor.tail, 0)

    def motor_dance_to_beat(this, msPerBeat=500):
        """Move the tail to the beat."""
        start_time = time.time()
        while this.current.process.poll() is None:  # While the subprocess is running
            elapsed_time = (time.time() - start_time) * 1000  # Milliseconds
            if int(elapsed_time / msPerBeat) % 2 == 0:
                this.toggle_tail()

            # Randomly move the mouth
            if random.random() > 0.9:
                this.toggle_mouth()

            if GPIOUtils.read_gpio(this.input.button):
                this.current.process.terminate()
                break

    def play_random_song(this):
        """Randomly select and play a song from ~/music."""
        if not this.audio.manifest:
            print("No songs found.")
            return None

        song_choice = random.choice(list(this.audio.manifest.keys()))
        song_path = os.path.expanduser(this.audio.manifest[song_choice]["path"])
        song_tempo = this.audio.manifest[song_choice]["tempo"]

        this.current.song = song_path
        this.current.tempo = song_tempo

        print(f"Playing song: {song_choice} ({song_path})")

        # Use cvlc to play the song
        command = [
            "sudo", "-u", "debian", "cvlc",
            "--alsa-audio-device=hw:1,0",
            f"--gain={this.audio.volume}",
            song_path
        ]
        try:
            this.current.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = this.current.process.communicate()  # Wait for the process
            if stderr:
                print("Error during playback:", stderr.decode())
        except Exception as e:
            print(f"Subprocess error: {e}")
            this.current.process = None

# Main Function
def main():
    performer = Fish()
    try:
        performer.worker()
    except Exception as e:
        print(f"Stopping: {e}")
    performer.destroy()

    # Just to be extra sure
    try:
        GPIOUtils.write_gpio(115, 0)
        GPIOUtils.write_gpio(20, 0)
    except:
        pass

if __name__ == "__main__":
    main()
