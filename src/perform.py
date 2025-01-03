import os
import random
import time
import json
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
        this.audio.volume = 0.2  # VLC gain value (e.g., 5% volume)

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
        this.current.song = eons.util.DotDict()
        this.current.song.path = None
        this.current.song.tempo = None
        this.current.song.length = None

        print("Initialization complete.")

    @staticmethod
    def static_cleanup():
        try:
            GPIOUtils.write_gpio(115, 0)
            GPIOUtils.write_gpio(20, 0)
        except:
            pass
        os.system("killall vlc")

        print("Static cleanup complete.")

    def cleanup(this):
        this.static_cleanup()

        this.current.song.path = None
        this.current.song.tempo = 0
        this.current.song.length = 0

        print("Cleanup complete.")

    def destroy(this):
        """Cleanup and destroy the object."""
        this.cleanup()

        GPIOUtils.write_gpio(this.pin.output.motor.tail, 0)
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 0)

        GPIOUtils.unexport_gpio(this.pin.output.motor.tail)
        GPIOUtils.unexport_gpio(this.pin.output.motor.mouth)
        GPIOUtils.unexport_gpio(this.input.button)

        print("Destruction complete.")

    def worker(this):
        """Main worker function."""
        print("Starting worker...")
        while True:
            if GPIOUtils.read_gpio(this.input.button):
                print("Button pressed!")
                if (this.current.song.path):
                    this.cleanup()
                else:
                    this.play_random_song()
                    this.motor_dance_to_beat(this.detect_tempo())
            time.sleep(0.5)

    def detect_tempo(this):
        """Detect the tempo (BPM) of the song."""
        print(f"Tempo for {this.current.song.path} is {this.current.song.tempo} ms / beat.")
        return this.current.song.tempo

    def toggle_mouth(this):
        """Toggle the mouth motor."""
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 1)
        time.sleep(0.14)
        GPIOUtils.write_gpio(this.pin.output.motor.mouth, 0)

    def toggle_tail(this):
        """Toggle the tail motor."""
        GPIOUtils.write_gpio(this.pin.output.motor.tail, 1)
        time.sleep(0.4)
        GPIOUtils.write_gpio(this.pin.output.motor.tail, 0)

    def motor_dance_to_beat(this, msPerBeat=500):
        """Move the tail to the beat."""
        start_time = time.time()
        elapsed_seconds = 0
        while elapsed_seconds <= this.current.song.length:
            elapsed_seconds = time.time() - start_time
            elapsed_milliseconds = elapsed_seconds * 1000 
            if int(elapsed_milliseconds / msPerBeat) % 2 == 0:
                # this.toggle_tail()
                this.toggle_mouth()

            # Randomly move the mouth
            # if random.random() > 0.2:
            #     this.toggle_mouth()

            if GPIOUtils.read_gpio(this.input.button):
                this.cleanup()
                break

            time.sleep(0.1)

    def play_random_song(this):
        """Randomly select and play a song from ~/music."""
        if not this.audio.manifest:
            print("No songs found.")
            return None

        song_choice = random.choice(list(this.audio.manifest.keys()))
        song_path = os.path.expanduser(this.audio.manifest[song_choice]["path"])
        song_tempo = this.audio.manifest[song_choice]["tempo"]
        song_length = this.audio.manifest[song_choice]["length"]

        this.current.song.path = song_path
        this.current.song.tempo = song_tempo
        this.current.song.length = song_length

        print(f"Playing song: {song_choice} ({song_path})")

        # Use cvlc to play the song
        command = f"sudo -u debian cvlc --alsa-audio-device=hw:1,0 --gain={this.audio.volume} '{this.current.song.path}' &"
        try:
            os.system(command)
        except Exception as e:
            print(f"Playback error: {e}")
            this.cleanup()

    def play_startup_audio(this):
        """Play the startup audio file."""
        startup_audio_path = os.path.expanduser("/home/debian/music/hi_dan_ready.mp3")
        print(f"Playing startup audio: {startup_audio_path}")
        command = f"sudo -u debian cvlc --alsa-audio-device=hw:1,0 --gain={this.audio.volume} '{startup_audio_path}' &"
        try:
            os.system(command)
            time.sleep(5)  # Ensure the audio finishes playing
            this.cleanup()
        except Exception as e:
            print(f"Startup audio error: {e}")

# Main Function
def main():
    performer = Fish()
    try:
        performer.play_startup_audio()
        performer.worker()
    except Exception as e:
        print(f"Stopping: {e}")
    performer.destroy()

    # Just to be extra sure
    Fish.static_cleanup()

if __name__ == "__main__":
    main()
