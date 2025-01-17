import pyaudio

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.device_name = "alsa_input.usb-MUSIC-BOOST_USB_Microphone_MB-306-00.mono-fallback"

    def list_devices(self):
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            print(f"Device {i}: {device_info['name']}")

    def start_recording(self):
        # Locate the microphone device by name
        device_index = None
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if self.device_name in device_info["name"]:
                device_index = i
                break

        if device_index is None:
            raise RuntimeError("Microphone USB non trouvé.")

        # Start recording
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=1024,
        )

    def stop_recording(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.audio.terminate()
